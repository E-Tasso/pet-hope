from uuid import UUID

from pydantic import BaseModel, Field


class ImageUploadResponse(BaseModel):
    """Schema for image upload response."""

    id: UUID
    animal_id: UUID
    original_url: str
    thumbnail_url: str
    is_primary: bool
    order: int

    class Config:
        from_attributes = True


class ImageResponse(BaseModel):
    """Schema for image response."""

    id: UUID
    animal_id: UUID
    original_url: str
    thumbnail_url: str
    is_primary: bool
    order: int

    class Config:
        from_attributes = True


class ImageSetPrimaryRequest(BaseModel):
    """Schema for setting an image as primary."""

    is_primary: bool = Field(
        True, description="Set to true to make this the primary image"
    )


class ImageReorderRequest(BaseModel):
    """Schema for reordering images."""

    image_orders: dict[UUID, int] = Field(
        ..., description="Map of image IDs to their new order values"
    )
