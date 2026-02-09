"""Product schema for request/response validation."""
from typing import Optional, List, TYPE_CHECKING
from pydantic import Field

from schemas.base_schema import BaseSchema
from schemas.category_schema import CategoryMinimalSchema 
from schemas.review_schema import ReviewNestedSchema 
from schemas.order_detail_schema import OrderDetailMinimalSchema

if TYPE_CHECKING:
    from schemas.category_schema import CategorySchema
    from schemas.order_detail_schema import OrderDetailSchema


class ProductSchema(BaseSchema):
    """Schema for Product entity with validations."""

    name: str = Field(..., min_length=1, max_length=200, description="Product name (required)")
    
    # 🎯 CAMBIO CLAVE: Vuelve a ser estricto (no nulo)
    price: float = Field(..., gt=0, description="Product price (must be greater than 0, required)")
    
    stock: int = Field(default=0, ge=0, description="Product stock quantity (must be >= 0)")

    # 🎯 CAMBIO CLAVE: Vuelve a ser estricto (no nulo)
    category_id: int = Field(..., description="Category ID reference (required)")

    category: Optional[CategoryMinimalSchema] = None 
    reviews: Optional[List[ReviewNestedSchema]] = []
    order_details: Optional[List[OrderDetailMinimalSchema]] = []