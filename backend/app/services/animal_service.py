from typing import Optional
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Animal, AnimalStatus, Image
from app.schemas import (
    AnimalCreate,
    AnimalFeedItem,
    AnimalFilters,
    AnimalListItem,
    AnimalResponse,
    AnimalStatusUpdate,
    AnimalUpdate,
    PaginatedResponse,
)
from app.schemas.animal import ImageInResponse
from app.utils.security import hash_key, verify_key


class AnimalService:
    """Service for animal-related business logic."""

    @staticmethod
    async def get_animals(
        db: AsyncSession,
        filters: AnimalFilters,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse[AnimalListItem]:
        """
        Get paginated list of animals with filters.

        Args:
            db: Database session
            filters: Filter parameters
            page: Page number (1-indexed)
            page_size: Items per page

        Returns:
            Paginated response with animal list items
        """
        # Build query
        query = select(Animal)

        # Apply filters
        if filters.species:
            query = query.where(Animal.species == filters.species)
        if filters.size:
            query = query.where(Animal.size == filters.size)
        if filters.gender:
            query = query.where(Animal.gender == filters.gender)
        if filters.status:
            query = query.where(Animal.status == filters.status)
        if filters.location:
            query = query.where(Animal.location.ilike(f"%{filters.location}%"))
        if filters.min_age_months is not None:
            query = query.where(Animal.age_months >= filters.min_age_months)
        if filters.max_age_months is not None:
            query = query.where(Animal.age_months <= filters.max_age_months)
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    Animal.name.ilike(search_term),
                    Animal.description.ilike(search_term),
                )
            )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        offset = (page - 1) * page_size
        query = query.order_by(Animal.created_at.desc()).offset(offset).limit(page_size)

        # Execute query
        result = await db.execute(query)
        animals = result.scalars().all()

        # Convert to list items with primary image
        items = []
        for animal in animals:
            primary_image = None
            if animal.images:
                # Find primary image or use first
                primary_image_obj = next(
                    (img for img in animal.images if img.is_primary), None
                ) or animal.images[0]
                primary_image = ImageInResponse.model_validate(primary_image_obj)

            item = AnimalListItem(
                id=animal.id,
                name=animal.name,
                species=animal.species,
                size=animal.size,
                gender=animal.gender,
                age_months=animal.age_months,
                location=animal.location,
                status=animal.status,
                primary_image=primary_image,
                created_at=animal.created_at,
            )
            items.append(item)

        # Calculate pages
        pages = (total + page_size - 1) // page_size if total > 0 else 0

        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    @staticmethod
    async def get_animals_feed(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 10,
    ) -> PaginatedResponse[AnimalFeedItem]:
        """
        Get paginated list of available animals for feed with all images.

        Args:
            db: Database session
            page: Page number (1-indexed)
            page_size: Items per page

        Returns:
            Paginated response with animal feed items
        """
        # Build query - only available animals for the feed
        query = select(Animal).where(Animal.status == AnimalStatus.AVAILABLE)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering (newest first)
        offset = (page - 1) * page_size
        query = query.order_by(Animal.created_at.desc()).offset(offset).limit(page_size)

        # Execute query
        result = await db.execute(query)
        animals = result.scalars().all()

        # Convert to feed items with all images
        items = []
        for animal in animals:
            # Sort images by order, primary first
            sorted_images = sorted(
                animal.images,
                key=lambda img: (not img.is_primary, img.order),
            )
            images = [ImageInResponse.model_validate(img) for img in sorted_images]

            item = AnimalFeedItem(
                id=animal.id,
                name=animal.name,
                species=animal.species,
                size=animal.size,
                gender=animal.gender,
                age_months=animal.age_months,
                description=animal.description,
                location=animal.location,
                status=animal.status,
                contact_info=animal.contact_info,
                images=images,
                created_at=animal.created_at,
            )
            items.append(item)

        # Calculate pages
        pages = (total + page_size - 1) // page_size if total > 0 else 0

        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    @staticmethod
    async def get_animal_by_id(db: AsyncSession, animal_id: UUID) -> Optional[Animal]:
        """
        Get animal by ID.

        Args:
            db: Database session
            animal_id: Animal ID

        Returns:
            Animal or None if not found
        """
        result = await db.execute(select(Animal).where(Animal.id == animal_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_animal(db: AsyncSession, animal_data: AnimalCreate) -> Animal:
        """
        Create a new animal.

        Args:
            db: Database session
            animal_data: Animal creation data

        Returns:
            Created animal
        """
        # Extract and hash the edit_key
        data_dict = animal_data.model_dump()
        edit_key = data_dict.pop("edit_key")
        data_dict["edit_key_hash"] = hash_key(edit_key)

        animal = Animal(**data_dict)
        db.add(animal)
        await db.flush()
        await db.refresh(animal)
        return animal

    @staticmethod
    def verify_edit_key(animal: Animal, edit_key: str) -> bool:
        """
        Verify if the provided edit key matches the animal's stored hash.

        Args:
            animal: Animal to verify
            edit_key: Plain text edit key

        Returns:
            True if key matches, False otherwise
        """
        if not animal.edit_key_hash:
            return False
        return verify_key(edit_key, animal.edit_key_hash)

    @staticmethod
    async def update_animal(
        db: AsyncSession, animal: Animal, animal_data: AnimalUpdate
    ) -> Animal:
        """
        Update an animal.

        Args:
            db: Database session
            animal: Animal to update
            animal_data: Update data (only provided fields)

        Returns:
            Updated animal
        """
        update_dict = animal_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(animal, field, value)

        await db.flush()
        await db.refresh(animal)
        return animal

    @staticmethod
    async def update_animal_status(
        db: AsyncSession, animal: Animal, status_data: AnimalStatusUpdate
    ) -> Animal:
        """
        Update animal status only.

        Args:
            db: Database session
            animal: Animal to update
            status_data: New status

        Returns:
            Updated animal
        """
        animal.status = status_data.status
        await db.flush()
        await db.refresh(animal)
        return animal

    @staticmethod
    async def delete_animal(db: AsyncSession, animal: Animal) -> None:
        """
        Delete an animal (and cascade delete its images).

        Args:
            db: Database session
            animal: Animal to delete
        """
        await db.delete(animal)
        await db.flush()

    @staticmethod
    async def get_available_species(db: AsyncSession) -> list[str]:
        """
        Get list of species that have animals.

        Args:
            db: Database session

        Returns:
            List of species values
        """
        result = await db.execute(select(Animal.species).distinct())
        species = [s.value for s in result.scalars().all()]
        return sorted(species)

    @staticmethod
    async def get_locations(db: AsyncSession) -> list[str]:
        """
        Get list of locations that have animals.

        Args:
            db: Database session

        Returns:
            List of unique locations
        """
        result = await db.execute(
            select(Animal.location).distinct().order_by(Animal.location)
        )
        return list(result.scalars().all())
