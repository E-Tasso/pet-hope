from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import AnimalStatus, Gender, Size, Species


class AnimalBase(BaseModel):
    """Base schema for Animal with common fields."""

    name: str = Field(..., min_length=1, max_length=100, description="Animal name")
    species: Species = Field(..., description="Animal species")
    breed: Optional[str] = Field(None, max_length=100, description="Breed (optional)")
    age_months: Optional[int] = Field(
        None, ge=0, le=360, description="Age in months (0-360)"
    )
    size: Size = Field(..., description="Animal size")
    gender: Gender = Field(..., description="Animal gender")
    description: str = Field(
        ..., min_length=10, max_length=5000, description="Animal description and history"
    )
    traits: List[str] = Field(
        default_factory=list,
        description="Characteristics (e.g., castrated, vaccinated, dewormed)",
    )
    special_needs: Optional[str] = Field(
        None, max_length=1000, description="Special needs or medical conditions"
    )
    location: str = Field(
        ..., min_length=1, max_length=100, description="City or region"
    )
    contact_info: dict = Field(
        ...,
        description="Contact information (phone, email, whatsapp, etc.)",
    )

    @field_validator("traits")
    @classmethod
    def validate_traits(cls, v: List[str]) -> List[str]:
        """Validate traits list."""
        if not isinstance(v, list):
            raise ValueError("traits must be a list")
        # Remove duplicates and empty strings
        return list(set(t.strip() for t in v if t.strip()))

    @field_validator("contact_info")
    @classmethod
    def validate_contact_info(cls, v: dict) -> dict:
        """Validate contact info has at least one contact method."""
        if not v:
            raise ValueError("contact_info must contain at least one contact method")
        return v


class AnimalCreate(AnimalBase):
    """Schema for creating a new animal."""

    status: AnimalStatus = Field(
        default=AnimalStatus.AVAILABLE,
        description="Initial status (defaults to available)",
    )
    edit_key: str = Field(
        ...,
        min_length=6,
        max_length=50,
        description="Key for editing this animal later (min 6 characters)",
    )


class AnimalUpdate(BaseModel):
    """Schema for updating an animal (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    species: Optional[Species] = None
    breed: Optional[str] = Field(None, max_length=100)
    age_months: Optional[int] = Field(None, ge=0, le=360)
    size: Optional[Size] = None
    gender: Optional[Gender] = None
    description: Optional[str] = Field(None, min_length=10, max_length=5000)
    traits: Optional[List[str]] = None
    special_needs: Optional[str] = Field(None, max_length=1000)
    location: Optional[str] = Field(None, min_length=1, max_length=100)
    contact_info: Optional[dict] = None
    status: Optional[AnimalStatus] = None

    @field_validator("traits")
    @classmethod
    def validate_traits(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate traits list."""
        if v is None:
            return None
        if not isinstance(v, list):
            raise ValueError("traits must be a list")
        return list(set(t.strip() for t in v if t.strip()))


class AnimalStatusUpdate(BaseModel):
    """Schema for updating only the animal status."""

    status: AnimalStatus = Field(..., description="New status")


class ImageInResponse(BaseModel):
    """Simplified image schema for animal responses."""

    id: UUID
    original_url: str
    thumbnail_url: str
    is_primary: bool
    order: int

    class Config:
        from_attributes = True


class AnimalResponse(AnimalBase):
    """Schema for animal response."""

    id: UUID
    status: AnimalStatus
    created_at: datetime
    updated_at: datetime
    images: List[ImageInResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class AnimalListItem(BaseModel):
    """Simplified schema for animal in list views."""

    id: UUID
    name: str
    species: Species
    size: Size
    gender: Gender
    age_months: Optional[int]
    location: str
    status: AnimalStatus
    primary_image: Optional[ImageInResponse] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AnimalFeedItem(BaseModel):
    """Schema for animal in feed view with all images."""

    id: UUID
    name: str
    species: Species
    size: Size
    gender: Gender
    age_months: Optional[int]
    description: str
    location: str
    status: AnimalStatus
    contact_info: dict
    images: List[ImageInResponse] = Field(default_factory=list)
    created_at: datetime

    class Config:
        from_attributes = True


class AnimalFilters(BaseModel):
    """Schema for filtering animals in list queries."""

    species: Optional[Species] = Field(None, description="Filter by species")
    size: Optional[Size] = Field(None, description="Filter by size")
    gender: Optional[Gender] = Field(None, description="Filter by gender")
    status: Optional[AnimalStatus] = Field(None, description="Filter by status")
    location: Optional[str] = Field(None, description="Filter by location (partial match)")
    min_age_months: Optional[int] = Field(None, ge=0, description="Minimum age in months")
    max_age_months: Optional[int] = Field(None, ge=0, description="Maximum age in months")
    search: Optional[str] = Field(None, description="Search in name and description")


class EditKeyVerify(BaseModel):
    """Schema for verifying edit key."""

    edit_key: str = Field(..., description="The edit key to verify")


class AnimalUpdateWithKey(AnimalUpdate):
    """Schema for updating an animal with edit key verification."""

    edit_key: str = Field(..., description="The edit key for verification")
