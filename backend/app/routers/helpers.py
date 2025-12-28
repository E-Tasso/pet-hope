from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import AnimalService

router = APIRouter(tags=["Helpers"])


@router.get("/species")
async def get_species(
    db: AsyncSession = Depends(get_db),
) -> list[str]:
    """
    Get list of species that currently have animals.

    Returns only species for which at least one animal exists.
    Useful for populating filter dropdowns.
    """
    return await AnimalService.get_available_species(db)


@router.get("/locations")
async def get_locations(
    db: AsyncSession = Depends(get_db),
) -> list[str]:
    """
    Get list of locations that currently have animals.

    Returns unique location values from all animals.
    Useful for populating location filters.
    """
    return await AnimalService.get_locations(db)
