from app.api.common.schemas.price.price_schema import PriceErrorResponse

UNPROCESSABLE_ENTITY_RESPONSE = {
    "description": "Error: Unprocessable Entity",
    "content": {
        "application/json": {
            "example": PriceErrorResponse.Config.json_schema_extra["unprocessable_entity"]
        }
    },
}

NOT_FOUND_RESPONSE = {
    "description": "Error: Not Found",
    "content": {
        "application/json": {
            "example": PriceErrorResponse.Config.json_schema_extra["not_found"]
        }
    },
}

BAD_REQUEST_RESPONSE = {
    "description": "Error: Bad Request",
    "content": {
        "application/json": {
            "example": PriceErrorResponse.Config.json_schema_extra["de"]
        }
    },
}

MISSING_HEADER_RESPONSE = {
    "description": "Header 'seller-id' obrigatório",
    "content": {
        "application/json": {
            "example": {
                "slug": "BAD_REQUEST",
                "message": "Bad Request",
                "details": [
                    {
                        "message": "Header 'seller-id' obrigatório",
                        "location": "header",
                        "slug": "missing_required_header",
                        "field": "seller-id",
                    }
                ],
            }
        }
    },
}
