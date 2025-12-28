from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.schemas import (
    AnimalCreate,
    AnimalFeedItem,
    AnimalFilters,
    AnimalListItem,
    AnimalResponse,
    AnimalStatusUpdate,
    AnimalUpdate,
    AnimalUpdateWithKey,
    EditKeyVerify,
    PaginatedResponse,
)
from app.services import AnimalService

settings = get_settings()
router = APIRouter(prefix="/animals", tags=["Animals"])


@router.get("", response_model=PaginatedResponse[AnimalListItem])
async def list_animals(
    # Filters
    species: str | None = Query(None, description="Filter by species"),
    size: str | None = Query(None, description="Filter by size"),
    gender: str | None = Query(None, description="Filter by gender"),
    status: str | None = Query(None, description="Filter by status"),
    location: str | None = Query(None, description="Filter by location (partial match)"),
    min_age_months: int | None = Query(None, ge=0, description="Minimum age in months"),
    max_age_months: int | None = Query(None, ge=0, description="Maximum age in months"),
    search: str | None = Query(None, description="Search in name and description"),
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(
        default=settings.default_page_size,
        ge=1,
        le=settings.max_page_size,
        description="Items per page",
    ),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[AnimalListItem]:
    """
    List animals with optional filters and pagination.

    Returns a paginated list of animals with their primary image.
    """
    filters = AnimalFilters(
        species=species,
        size=size,
        gender=gender,
        status=status,
        location=location,
        min_age_months=min_age_months,
        max_age_months=max_age_months,
        search=search,
    )

    return await AnimalService.get_animals(db, filters, page, page_size)


@router.get("/feed", response_model=PaginatedResponse[AnimalFeedItem])
async def get_animals_feed(
    # Filters
    species: str | None = Query(None, description="Filter by species"),
    size: str | None = Query(None, description="Filter by size"),
    gender: str | None = Query(None, description="Filter by gender"),
    location: str | None = Query(None, description="Filter by location (partial match)"),
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Items per page",
    ),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[AnimalFeedItem]:
    """
    Get animals for the feed with all images.

    Returns a paginated list of available animals with their full image galleries.
    Optimized for infinite scroll feed display.
    """
    filters = AnimalFilters(
        species=species,
        size=size,
        gender=gender,
        location=location,
    )
    return await AnimalService.get_animals_feed(db, filters, page, page_size)


@router.get("/{animal_id}", response_model=AnimalResponse)
async def get_animal(
    animal_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> AnimalResponse:
    """
    Get a single animal by ID.

    Returns full animal details including all images.
    """
    animal = await AnimalService.get_animal_by_id(db, animal_id)
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Animal {animal_id} not found",
        )

    return AnimalResponse.model_validate(animal)


@router.post("/{animal_id}/verify-key")
async def verify_edit_key(
    animal_id: UUID,
    key_data: EditKeyVerify,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Verify if the provided edit key is valid for the animal.

    Returns {"valid": true/false} indicating if the key matches.
    """
    animal = await AnimalService.get_animal_by_id(db, animal_id)
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Animal {animal_id} not found",
        )

    is_valid = AnimalService.verify_edit_key(animal, key_data.edit_key)
    return {"valid": is_valid}


@router.put("/{animal_id}/edit", response_model=AnimalResponse)
async def update_animal_with_key(
    animal_id: UUID,
    animal_data: AnimalUpdateWithKey,
    db: AsyncSession = Depends(get_db),
) -> AnimalResponse:
    """
    Update an animal with edit key verification.

    Requires the correct edit_key to authorize the update.
    """
    animal = await AnimalService.get_animal_by_id(db, animal_id)
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Animal {animal_id} not found",
        )

    # Verify the edit key
    if not AnimalService.verify_edit_key(animal, animal_data.edit_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid edit key",
        )

    # Create AnimalUpdate without the edit_key field
    update_data = AnimalUpdate(**animal_data.model_dump(exclude={"edit_key"}, exclude_unset=True))

    updated_animal = await AnimalService.update_animal(db, animal, update_data)
    await db.commit()
    return AnimalResponse.model_validate(updated_animal)


@router.post("", response_model=AnimalResponse, status_code=status.HTTP_201_CREATED)
async def create_animal(
    animal_data: AnimalCreate,
    db: AsyncSession = Depends(get_db),
) -> AnimalResponse:
    """
    Create a new animal.

    Creates an animal record. Images can be uploaded separately.
    """
    animal = await AnimalService.create_animal(db, animal_data)
    await db.commit()
    return AnimalResponse.model_validate(animal)


@router.put("/{animal_id}", response_model=AnimalResponse)
async def update_animal(
    animal_id: UUID,
    animal_data: AnimalUpdate,
    db: AsyncSession = Depends(get_db),
) -> AnimalResponse:
    """
    Update an animal.

    All fields are optional - only provided fields will be updated.
    """
    animal = await AnimalService.get_animal_by_id(db, animal_id)
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Animal {animal_id} not found",
        )

    updated_animal = await AnimalService.update_animal(db, animal, animal_data)
    await db.commit()
    return AnimalResponse.model_validate(updated_animal)


@router.patch("/{animal_id}/status", response_model=AnimalResponse)
async def update_animal_status(
    animal_id: UUID,
    status_data: AnimalStatusUpdate,
    db: AsyncSession = Depends(get_db),
) -> AnimalResponse:
    """
    Update only the animal's adoption status.

    Useful for quickly marking animals as in_process or adopted.
    """
    animal = await AnimalService.get_animal_by_id(db, animal_id)
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Animal {animal_id} not found",
        )

    updated_animal = await AnimalService.update_animal_status(db, animal, status_data)
    await db.commit()
    return AnimalResponse.model_validate(updated_animal)


@router.delete("/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_animal(
    animal_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete an animal.

    This will also delete all associated images (cascade delete).
    """
    animal = await AnimalService.get_animal_by_id(db, animal_id)
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Animal {animal_id} not found",
        )

    await AnimalService.delete_animal(db, animal)
    await db.commit()
