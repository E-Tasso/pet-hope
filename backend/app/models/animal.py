import enum
from typing import List, Optional

from sqlalchemy import Enum, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Species(str, enum.Enum):
    """Animal species enum - based on IBAMA Portaria 93/1998."""

    DOG = "dog"
    CAT = "cat"
    RABBIT = "rabbit"
    HAMSTER = "hamster"
    GUINEA_PIG = "guinea_pig"
    BIRD = "bird"
    CHINCHILLA = "chinchilla"
    FISH = "fish"


class Size(str, enum.Enum):
    """Animal size enum."""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class Gender(str, enum.Enum):
    """Animal gender enum."""

    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class AnimalStatus(str, enum.Enum):
    """Animal adoption status enum."""

    AVAILABLE = "available"
    IN_PROCESS = "in_process"
    ADOPTED = "adopted"


class Animal(Base, UUIDMixin, TimestampMixin):
    """Animal model for pets available for adoption."""

    __tablename__ = "animals"

    # Basic information
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    species: Mapped[Species] = mapped_column(
        Enum(Species, values_callable=lambda x: [e.value for e in x]),
        nullable=False, index=True
    )
    breed: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    age_months: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Physical characteristics
    size: Mapped[Size] = mapped_column(
        Enum(Size, values_callable=lambda x: [e.value for e in x]),
        nullable=False, index=True
    )
    gender: Mapped[Gender] = mapped_column(
        Enum(Gender, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )

    # Description
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Status
    status: Mapped[AnimalStatus] = mapped_column(
        Enum(AnimalStatus, values_callable=lambda x: [e.value for e in x]),
        default=AnimalStatus.AVAILABLE,
        nullable=False,
        index=True,
    )

    # Characteristics (castrated, vaccinated, etc.)
    # Stored as JSON array of strings
    traits: Mapped[List[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        server_default="[]",
    )

    # Special needs
    special_needs: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Location
    location: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Contact information (stored as JSON)
    # Example: {"phone": "123456789", "email": "contact@example.com", "whatsapp": "123456789"}
    contact_info: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    # Edit key hash for allowing edits without login
    edit_key_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    images: Mapped[List["Image"]] = relationship(
        "Image",
        back_populates="animal",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="Image.order",
    )

    def __repr__(self) -> str:
        return f"<Animal(id={self.id}, name={self.name}, species={self.species})>"
