from pydantic import BaseModel


class Product(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    stock: int
    category: int


class Category(BaseModel):
    name: str
    parent_id: int | None = None
