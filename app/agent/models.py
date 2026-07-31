from typing import List, Optional
from pydantic import BaseModel, Field

class Planner(BaseModel):
    product_name: List[str] = Field(..., description="The name of each product extracted from the user message.")
    categories: List[str] = Field(..., description="List of product categories extracted from the user message.")
    budget: str = Field(..., description="The user's overall budget for shopping.")


class Product(BaseModel):
    name: str = Field(..., description="Name/title of the product as listed by the seller.")
    price: Optional[str] = Field(None, description="Price of the product, if available.")
    purchase_link: Optional[str] = Field(None, description="Direct URL where the user can buy this exact product (not a homepage or search page). Use null if no direct purchase link was found.")
    source: Optional[str] = Field(None, description="Name of the retailer/website selling the product.")
    description: Optional[str] = Field(None, description="Short one-sentence description of the product.")


class SearchOutput(BaseModel):
    query: str = Field(..., description="The search query used to find these products.")
    products: List[Product] = Field(..., description="Products matching what the user wants to buy, each with a direct purchase link.")


class Recommendation(BaseModel):
    product_name: str = Field(..., description="The recommended product.")
    reason: str = Field(..., description="Why this product was chosen.")
    purchase_link: Optional[str] = Field(None, description="Direct purchase link. Use null if no direct purchase link was found.")
    price: Optional[str] = Field(None)
    source: Optional[str] = Field(None)


class ExecuterOutput(BaseModel):
    recommendation: List[Recommendation]
    summary: str = Field(..., description="Overall shopping recommendation")