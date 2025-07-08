from pydantic import BaseModel


class PriceSuggestionResponse(BaseModel):
    job_id: str
    status: str
    suggested_price: str | None = None

    class Config:
        json_schema_extra = {"example": {"job_id": "1234567890abcdef", "status": "pending", "suggested_price": "123"}}
