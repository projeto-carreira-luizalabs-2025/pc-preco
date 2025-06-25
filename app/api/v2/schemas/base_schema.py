from pydantic import BaseModel, Field


class SellerSkuBaseModel(BaseModel):
    seller_id: str = Field(..., description="ID do seller")
    sku: str = Field(..., description="ID do produto do seller")


class SkuBaseModel(BaseModel):
    sku: str = Field(..., description="ID do produto do seller")
