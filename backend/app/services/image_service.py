from typing import BinaryIO, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Animal, Image
from app.services.storage import get_storage_service


class ImageService:
    """Service for image-related business logic."""

    @staticmethod
    async def upload_image(
        db: AsyncSession,
        animal_id: UUID,
        file: BinaryIO,
        content_type: str,
    ) -> Image:
        """
        Upload an image for an animal.

        Args:
            db: Database session
            animal_id: Animal ID
            file: Binary file data
            content_type: MIME type

        Returns:
            Created image record

        Raises:
            ValueError: If upload fails or animal not found
        """
        # Verify animal exists
        result = await db.execute(select(Animal).where(Animal.id == animal_id))
        animal = result.scalar_one_or_none()
        if not animal:
            raise ValueError(f"Animal {animal_id} not found")

        # Upload to storage
        storage = get_storage_service()
        urls = storage.upload_image(file, content_type)

        # Get current max order for this animal
        order_result = await db.execute(
            select(Image.order)
            .where(Image.animal_id == animal_id)
            .order_by(Image.order.desc())
            .limit(1)
        )
        max_order = order_result.scalar_one_or_none() or -1
        new_order = max_order + 1

        # Check if animal has no images (make first one primary)
        is_first_image = len(animal.images) == 0

        # Create image record
        image = Image(
            animal_id=animal_id,
            original_url=urls["original"],
            thumbnail_url=urls.get("thumbnail", urls["original"]),
            is_primary=is_first_image,
            order=new_order,
        )
        db.add(image)
        await db.flush()
        await db.refresh(image)

        return image

    @staticmethod
    async def get_image_by_id(db: AsyncSession, image_id: UUID) -> Optional[Image]:
        """
        Get image by ID.

        Args:
            db: Database session
            image_id: Image ID

        Returns:
            Image or None if not found
        """
        result = await db.execute(select(Image).where(Image.id == image_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_image(db: AsyncSession, image: Image) -> None:
        """
        Delete an image from database and storage.

        Args:
            db: Database session
            image: Image to delete
        """
        # Delete from storage
        storage = get_storage_service()
        try:
            storage.delete_image(image.original_url)
            if image.thumbnail_url != image.original_url:
                storage.delete_image(image.thumbnail_url)
        except Exception as e:
            # Log but don't fail if storage deletion fails
            print(f"Warning: Failed to delete image from storage: {e}")

        # Delete from database
        await db.delete(image)
        await db.flush()

    @staticmethod
    async def set_primary_image(
        db: AsyncSession, image: Image, is_primary: bool = True
    ) -> Image:
        """
        Set an image as primary (or not).

        If setting as primary, unsets other images for the same animal.

        Args:
            db: Database session
            image: Image to update
            is_primary: Whether to set as primary

        Returns:
            Updated image
        """
        if is_primary:
            # Unset other primary images for this animal
            await db.execute(
                update(Image)
                .where(Image.animal_id == image.animal_id)
                .where(Image.id != image.id)
                .values(is_primary=False)
            )

        image.is_primary = is_primary
        await db.flush()
        await db.refresh(image)
        return image

    @staticmethod
    async def reorder_images(
        db: AsyncSession, image_orders: dict[UUID, int]
    ) -> list[Image]:
        """
        Reorder images by updating their order values.

        Args:
            db: Database session
            image_orders: Map of image IDs to new order values

        Returns:
            List of updated images
        """
        updated_images = []
        for image_id, order in image_orders.items():
            result = await db.execute(select(Image).where(Image.id == image_id))
            image = result.scalar_one_or_none()
            if image:
                image.order = order
                updated_images.append(image)

        await db.flush()
        for image in updated_images:
            await db.refresh(image)

        return updated_images
