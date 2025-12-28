import io
import uuid
from pathlib import Path
from typing import BinaryIO, Optional

from minio import Minio
from minio.error import S3Error
from PIL import Image

from app.config import get_settings

settings = get_settings()


class StorageService:
    """Service for handling file storage operations with MinIO/S3."""

    def __init__(self):
        """Initialize MinIO client."""
        self.client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_use_ssl,
        )
        self.bucket = settings.minio_bucket
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        """Create bucket if it doesn't exist."""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                # Set bucket policy to public read for images
                policy = f"""{{
                    "Version": "2012-10-17",
                    "Statement": [
                        {{
                            "Effect": "Allow",
                            "Principal": {{"AWS": ["*"]}},
                            "Action": ["s3:GetObject"],
                            "Resource": ["arn:aws:s3:::{self.bucket}/*"]
                        }}
                    ]
                }}"""
                self.client.set_bucket_policy(self.bucket, policy)
        except S3Error as e:
            print(f"Error ensuring bucket exists: {e}")

    def upload_image(
        self,
        file: BinaryIO,
        content_type: str,
        generate_thumbnail: bool = True,
    ) -> dict[str, str]:
        """
        Upload an image to storage.

        Args:
            file: Binary file object
            content_type: MIME type of the file
            generate_thumbnail: Whether to generate a thumbnail

        Returns:
            dict with 'original' and 'thumbnail' URLs

        Raises:
            ValueError: If file is not a valid image or too large
        """
        # Validate file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning

        if file_size > settings.max_image_size_bytes:
            raise ValueError(
                f"File too large. Max size: {settings.max_image_size_mb}MB"
            )

        # Validate image
        try:
            img = Image.open(file)
            img.verify()
            file.seek(0)
            img = Image.open(file)
        except Exception as e:
            raise ValueError(f"Invalid image file: {str(e)}")

        # Generate unique filename
        file_id = str(uuid.uuid4())
        ext = Path(content_type.split("/")[-1]).suffix or ".jpg"
        if not ext.startswith("."):
            ext = f".{ext}"

        original_key = f"originals/{file_id}{ext}"
        thumbnail_key = f"thumbnails/{file_id}{ext}"

        urls = {}

        # Upload original
        file.seek(0)
        self.client.put_object(
            bucket_name=self.bucket,
            object_name=original_key,
            data=file,
            length=file_size,
            content_type=content_type,
        )
        urls["original"] = self._get_public_url(original_key)

        # Generate and upload thumbnail
        if generate_thumbnail:
            thumbnail_bytes = self._create_thumbnail(img)
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=thumbnail_key,
                data=thumbnail_bytes,
                length=len(thumbnail_bytes.getvalue()),
                content_type=content_type,
            )
            urls["thumbnail"] = self._get_public_url(thumbnail_key)

        return urls

    def _create_thumbnail(self, img: Image.Image) -> io.BytesIO:
        """
        Create a thumbnail from an image.

        Args:
            img: PIL Image object

        Returns:
            BytesIO buffer containing thumbnail
        """
        # Convert RGBA to RGB if necessary
        if img.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = background

        # Create thumbnail
        img.thumbnail(settings.thumbnail_size, Image.Resampling.LANCZOS)

        # Save to bytes buffer
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85, optimize=True)
        buffer.seek(0)

        return buffer

    def delete_image(self, url: str) -> None:
        """
        Delete an image from storage.

        Args:
            url: Full URL or object key
        """
        # Extract object key from URL
        object_key = url.split(f"{self.bucket}/")[-1]

        try:
            self.client.remove_object(self.bucket, object_key)
        except S3Error as e:
            print(f"Error deleting image {object_key}: {e}")

    def _get_public_url(self, object_key: str) -> str:
        """
        Get public URL for an object.

        Args:
            object_key: Object key in bucket

        Returns:
            Public URL
        """
        # Use public URL if configured (for Docker setups where internal != external hostname)
        # The public URL should already include the bucket path (e.g., /storage -> /pethope-images)
        if settings.minio_public_url:
            base_url = settings.minio_public_url.rstrip("/")
            return f"{base_url}/{object_key}"

        # Fallback to endpoint-based URL
        protocol = "https" if settings.minio_use_ssl else "http"
        return f"{protocol}://{settings.minio_endpoint}/{self.bucket}/{object_key}"

    def health_check(self) -> bool:
        """
        Check if storage service is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            return self.client.bucket_exists(self.bucket)
        except Exception:
            return False


# Singleton instance
_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """
    Get or create storage service instance.

    Returns:
        StorageService instance
    """
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
