from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field

# Re-export enums for convenience
from app.models.animal import AnimalStatus, Gender, Size, Species

__all__ = ["Species", "Size", "Gender", "AnimalStatus", "PaginatedResponse"]


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema."""

    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Items per page")
    pages: int = Field(..., ge=0, description="Total number of pages")

    class Config:
        from_attributes = True
