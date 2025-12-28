from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import ImageReorderRequest, ImageSetPrimaryRequest, ImageUploadResponse
from app.services import ImageService

router = APIRouter(prefix="/images", tags=["Images"])


@router.post(
    "/animals/{animal_id}/images",
    response_model=ImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_image(
    animal_id: UUID,
    file: UploadFile = File(..., description="Image file (max 5MB)"),
    db: AsyncSession = Depends(get_db),
) -> ImageUploadResponse:
    """
    Upload an image for an animal.

    Accepts JPG, PNG, or WebP images up to 5MB.
    Automatically generates a thumbnail (400x400).
    First image uploaded becomes the primary image.
    """
    # Validate content type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image (JPG, PNG, or WebP)",
        )

    try:
        # Upload image
        image = await ImageService.upload_image(
            db, animal_id, file.file, file.content_type
        )
        await db.commit()
        return ImageUploadResponse.model_validate(image)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}",
        )


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete an image.

    Removes the image from both storage and database.
    """
    image = await ImageService.get_image_by_id(db, image_id)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image {image_id} not found",
        )

    await ImageService.delete_image(db, image)
    await db.commit()


@router.patch("/{image_id}/primary", response_model=ImageUploadResponse)
async def set_primary_image(
    image_id: UUID,
    request: ImageSetPrimaryRequest,
    db: AsyncSession = Depends(get_db),
) -> ImageUploadResponse:
    """
    Set an image as the primary image for its animal.

    When set to true, unsets any other primary images for the same animal.
    """
    image = await ImageService.get_image_by_id(db, image_id)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image {image_id} not found",
        )

    updated_image = await ImageService.set_primary_image(
        db, image, request.is_primary
    )
    await db.commit()
    return ImageUploadResponse.model_validate(updated_image)


@router.post("/reorder", response_model=list[ImageUploadResponse])
async def reorder_images(
    request: ImageReorderRequest,
    db: AsyncSession = Depends(get_db),
) -> list[ImageUploadResponse]:
    """
    Reorder images by providing a map of image IDs to order values.

    Used for drag-and-drop reordering in the admin interface.
    """
    updated_images = await ImageService.reorder_images(db, request.image_orders)
    await db.commit()
    return [ImageUploadResponse.model_validate(img) for img in updated_images]
