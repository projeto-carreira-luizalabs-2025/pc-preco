from app.api.v2.schemas.price_schema import PriceErrorResponse

APPLICATION_JSON = "application/json"

UNPROCESSABLE_ENTITY_RESPONSE = {
    "description": "Error: Unprocessable Entity",
    "content": {APPLICATION_JSON: {"example": PriceErrorResponse.Config.json_schema_extra["unprocessable_entity"]}},
}

NOT_FOUND_RESPONSE = {
    "description": "Error: Not Found",
    "content": {APPLICATION_JSON: {"example": PriceErrorResponse.Config.json_schema_extra["not_found"]}},
}

HISTORY_NOT_FOUND_RESPONSE = {
    "description": "Error: Not Found",
    "content": {APPLICATION_JSON: {"example": PriceErrorResponse.Config.json_schema_extra["history_not_found"]}},
}

BAD_REQUEST_RESPONSE = {
    "description": "Error: Bad Request",
    "content": {APPLICATION_JSON: {"example": PriceErrorResponse.Config.json_schema_extra["de"]}},
}

MISSING_HEADER_RESPONSE = {
    "description": "Header 'seller-id' obrigatório",
    "content": {
        APPLICATION_JSON: {
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
