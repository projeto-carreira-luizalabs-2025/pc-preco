from typing import TYPE_CHECKING

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from app.api.common.schemas import ListResponse, Paginator, get_request_pagination
from app.api.v2.schemas.price_schema import (
    PriceCreate,
    PriceErrorResponse,
    PricePatch,
    PriceResponse,
    PriceUpdate,
)
from app.container import Container

from . import PRICE_PREFIX

if TYPE_CHECKING:
    from app.services import PriceService


router = APIRouter(prefix=PRICE_PREFIX, tags=["Preços (v1)"])


# Recupera lista de precificações
@router.get(
    "",
    response_model=ListResponse[PriceResponse],
    status_code=status.HTTP_200_OK,
    summary="Recuperar lista de precificações",
    responses={
        422: {
            "description": "Error: Unprocessable Entity",
            "content": {
                "application/json": {"example": PriceErrorResponse.Config.json_schema_extra["unprocessable_entity"]}
            },
        },
    },
)
@inject
async def get(
    paginator: Paginator = Depends(get_request_pagination),
    price_service: "PriceService" = Depends(Provide[Container.price_service]),
):
    results = await price_service.find(paginator=paginator, filters={})

    return paginator.paginate(results=results)


# Busca precificação por "seller_id" e "sku"
@router.get(
    "/{seller_id}/{sku}",
    response_model=PriceResponse,
    status_code=status.HTTP_200_OK,
    summary="Recuperar precificação por seller_id e sku",
    responses={
        404: {
            "description": "Error: Not Found",
            "content": {"application/json": {"example": PriceErrorResponse.Config.json_schema_extra["not_found"]}},
        },
    },
)
@inject
async def get_by_seller_id_and_sku(
    seller_id: str,
    sku: str,
    price_service: "PriceService" = Depends(Provide[Container.price_service]),
):
    return await price_service.get_by_seller_id_and_sku(seller_id=seller_id, sku=sku)


# Cria uma precificação
@router.post(
    "",
    response_model=PriceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar precificação",
    responses={
        400: {
            "description": "Error: Bad Request",
            "content": {"application/json": {"example": PriceErrorResponse.Config.json_schema_extra["de"]}},
        },
    },
)
@inject
async def create(price: PriceCreate, price_service: "PriceService" = Depends(Provide[Container.price_service])):
    from app.models import Price

    price_model = Price(**price.model_dump())
    return await price_service.create(price_model)


# Atualiza uma precificação por "seller_id" e "sku"
@router.put(
    "/{seller_id}/{sku}",
    response_model=PriceResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar precificação por seller_id e sku",
    responses={
        404: {
            "description": "Error: Not Found",
            "content": {"application/json": {"example": PriceErrorResponse.Config.json_schema_extra["not_found"]}},
        },
        400: {
            "description": "Error: Bad Request",
            "content": {"application/json": {"example": PriceErrorResponse.Config.json_schema_extra["de"]}},
        },
    },
)
@inject
async def replace(
    seller_id: str,
    sku: str,
    price: PriceUpdate,
    price_service: "PriceService" = Depends(Provide[Container.price_service]),
):
    from app.models import Price

    price_model = Price(seller_id=seller_id, sku=sku, **price.model_dump())
    entity_id = f"{seller_id}|{sku}"
    return await price_service.update(entity_id, price_model)


# Atualiza parcialmente uma precificação por "seller_id" e "sku"
@router.patch(
    "/{seller_id}/{sku}",
    response_model=PriceResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar parcialmente precificação por seller_id e sku",
    responses={
        404: {
            "description": "Error: Not Found",
            "content": {"application/json": {"example": PriceErrorResponse.Config.json_schema_extra["not_found"]}},
        },
        400: {
            "description": "Error: Bad Request",
            "content": {"application/json": {"example": PriceErrorResponse.Config.json_schema_extra["de"]}},
        },
    },
)
@inject
async def patch(
    seller_id: str,
    sku: str,
    price_update_data: PricePatch,
    price_service: "PriceService" = Depends(Provide[Container.price_service]),
):
    update_data = price_update_data.model_dump(exclude_unset=True)
    entity_id = f"{seller_id}|{sku}"
    return await price_service.patch(entity_id, update_data)


# Deleta uma precificação por "seller_id" e "sku"
@router.delete(
    "/{seller_id}/{sku}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir precificação por seller_id e sku",
    responses={
        404: {
            "description": "Error: Not Found",
            "content": {"application/json": {"example": PriceErrorResponse.Config.json_schema_extra["not_found"]}},
        },
    },
)
@inject
async def delete(seller_id: str, sku: str, price_service: "PriceService" = Depends(Provide[Container.price_service])):
    await price_service.delete(seller_id, sku)
