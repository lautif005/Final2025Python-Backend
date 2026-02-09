from typing import Optional, TYPE_CHECKING
from pydantic import Field

from schemas.base_schema import BaseSchema

# --- 1. ESQUEMA SIMPLIFICADO PARA ANIDAMIENTO (Rompe el ciclo) ---
class ReviewNestedSchema(BaseSchema):
    """Product review schema for use within other schemas (e.g., Product). 
    Excludes product reference to prevent recursion."""

    rating: float = Field(
        ...,
        ge=1.0,
        le=5.0,
        description="Rating from 1 to 5 stars (required)"
    )

    comment: Optional[str] = Field(
        None,
        min_length=10,
        max_length=1000,
        description="Review comment (optional, 10-1000 characters)"
    )
    # NO INCLUIR product ni product_id


if TYPE_CHECKING:
    from schemas.product_schema import ProductSchema


# --- 2. ESQUEMA COMPLETO (Para endpoints CRUD de Reseñas) ---
class ReviewSchema(BaseSchema):
    """Product review schema with validation"""

    rating: float = Field(
        ...,
        ge=1.0,
        le=5.0,
        description="Rating from 1 to 5 stars (required)"
    )

    comment: Optional[str] = Field(
        None,
        min_length=10,
        max_length=1000,
        description="Review comment (optional, 10-1000 characters)"
    )

    product_id: int = Field(
        ...,
        description="Product ID reference (required)"
    )

    product: Optional['ProductSchema'] = None
    product: Optional['ProductSchema'] = None