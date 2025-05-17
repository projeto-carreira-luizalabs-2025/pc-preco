from typing import TYPE_CHECKING

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from app.api.common.schemas import ListResponse, Paginator, UuidType, get_request_pagination
from app.container import Container

from ..schemas.price_schema import PriceCreate, PriceResponse, PriceUpdate, PriceErrorResponse
from . import PRICE_PREFIX

if TYPE_CHECKING:
    from app.services import PriceService


router = APIRouter(prefix=PRICE_PREFIX, tags=["Preços"])


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


# Cria uma precificação para um produto
@router.post(
    "",
    response_model=PriceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar precificação",
    responses={
        400: {
            "description": "Error: Bad Request",
            "content": {"application/json": {"example": PriceErrorResponse.Config.json_schema_extra["preco_de"]}},
        },
    },
)
@inject
async def create(price: PriceCreate, price_service: "PriceService" = Depends(Provide[Container.price_service])):
    return await price_service.create_price(price)


@router.patch(
    "/{seller_id}/{sku}",
    response_model=PriceResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar precificação",
    responses={
        404: {
            "description": "Error: Not Found",
            "content": {"application/json": {"example": PriceErrorResponse.Config.json_schema_extra["not_found"]}},
        },
        400: {
            "description": "Error: Bad Request",
            "content": {"application/json": {"example": PriceErrorResponse.Config.json_schema_extra["preco_de"]}},
        },
    },
)
@inject
async def update_by_seller_id_and_sku(
    seller_id: str,
    sku: str,
    price: PriceUpdate,
    price_service: "PriceService" = Depends(Provide[Container.price_service]),
):
    return await price_service.update_price(seller_id, sku, price)


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
async def delete_by_seller_id_and_sku(
    seller_id: str, sku: str, price_service: "PriceService" = Depends(Provide[Container.price_service])
):
    await price_service.delete_by_seller_id_and_sku(seller_id, sku)
