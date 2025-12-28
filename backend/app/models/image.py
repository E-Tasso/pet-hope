import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin

if TYPE_CHECKING:
    from app.models.animal import Animal


class Image(Base, UUIDMixin):
    """Image model for animal photos."""

    __tablename__ = "images"

    # Foreign key to animal
    animal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("animals.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Image URLs (original and thumbnail)
    original_url: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_url: Mapped[str] = mapped_column(String(500), nullable=False)

    # Primary image flag
    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    # Display order
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationship
    animal: Mapped["Animal"] = relationship(
        "Animal",
        back_populates="images",
    )

    def __repr__(self) -> str:
        return f"<Image(id={self.id}, animal_id={self.animal_id}, is_primary={self.is_primary})>"
