"""Pydantic schemas for request/response validation."""

from app.schemas.animal import (
    AnimalCreate,
    AnimalFeedItem,
    AnimalFilters,
    AnimalListItem,
    AnimalResponse,
    AnimalStatusUpdate,
    AnimalUpdate,
    AnimalUpdateWithKey,
    EditKeyVerify,
)
from app.schemas.common import AnimalStatus, Gender, PaginatedResponse, Size, Species
from app.schemas.image import (
    ImageReorderRequest,
    ImageResponse,
    ImageSetPrimaryRequest,
    ImageUploadResponse,
)

__all__ = [
    # Enums
    "Species",
    "Size",
    "Gender",
    "AnimalStatus",
    # Common
    "PaginatedResponse",
    # Animal
    "AnimalCreate",
    "AnimalUpdate",
    "AnimalUpdateWithKey",
    "AnimalStatusUpdate",
    "AnimalResponse",
    "AnimalListItem",
    "AnimalFeedItem",
    "AnimalFilters",
    "EditKeyVerify",
    # Image
    "ImageResponse",
    "ImageUploadResponse",
    "ImageSetPrimaryRequest",
    "ImageReorderRequest",
]
