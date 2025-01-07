from typing import Optional
from pydantic import BaseModel

class ProductSchema(BaseModel):
    milvus_id: Optional[str] = None 
    category: str
    name: str
    price: int
    link: str  # Chuyển từ HttpUrl thành str
    price_raw: Optional[str] = None
    img: str  # Chuyển từ HttpUrl thành str
    description: Optional[str] = None
    ingredients: Optional[str] = None
    instructions: Optional[str] = None
    specifications: Optional[str] = None
    skin_type: Optional[str] = None
    rating: Optional[float] = None
    comments: Optional[str] = None
    color: Optional[str] = None
    stock: bool
    volume_weight: Optional[float] = None
    brand: str
    
    def get_embedding_fields(self):
        return {
            "name": self.name,
            "description": self.description,
            "ingredients": self.ingredients,
            "instructions": self.instructions,
            "comments": self.comments
        }