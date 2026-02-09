"""Category schema with validation."""
from typing import Optional, List, TYPE_CHECKING
from pydantic import Field

from schemas.base_schema import BaseSchema

if TYPE_CHECKING:
    from schemas.product_schema import ProductSchema


class CategoryMinimalSchema(BaseSchema): # AÑADIR ESTA CLASE
    """Minimal schema for Category, used in nested responses (e.g., Product)."""
    id_key: int 
    name: str 

# El esquema completo de Category
class CategorySchema(BaseSchema):
    """Schema for Category entity with validations."""

    name: str = Field(..., min_length=1, max_length=100, description="Category name (required, unique)")
    products: Optional[List['ProductSchema']] = []