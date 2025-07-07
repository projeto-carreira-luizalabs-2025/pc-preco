from typing import TYPE_CHECKING, Optional
from fastapi import Query
import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from app.api.common.auth_handler import do_auth, UserAuthInfo, get_current_user
from app.api.common.dependencies import get_required_seller_id
from app.api.common.responses.price_responses import (
    BAD_REQUEST_RESPONSE,
    MISSING_HEADER_RESPONSE,
    NOT_FOUND_RESPONSE,
    HISTORY_NOT_FOUND_RESPONSE,
    UNPROCESSABLE_ENTITY_RESPONSE,
)
from app.api.common.schemas import ListResponse, Paginator, get_request_pagination
from app.api.v2.schemas.price_history_schema import PriceHistoryListResponse
from app.api.v2.schemas.price_suggestion_schema import PriceSuggestionResponse
from app.api.v2.schemas.price_schema import PriceCreate, PricePatch, PriceResponse, PriceUpdate
from app.container import Container
from app.models import Price
from app.services.price_history_service import PriceHistoryService

from . import PRICE_PREFIX

if TYPE_CHECKING:
    from app.services import PriceService


router = APIRouter(prefix=PRICE_PREFIX, tags=["Preços (v2)"], dependencies=[Depends(do_auth)])

logger = logging.getLogger(__name__)


# Recupera lista de precificações
@router.get(
    "",
    response_model=ListResponse[PriceResponse],
    status_code=status.HTTP_200_OK,
    summary="Recuperar lista de precificações",
    responses={422: UNPROCESSABLE_ENTITY_RESPONSE},
)
@inject
async def get(
    seller_id: str = Depends(get_required_seller_id),
    paginator: Paginator = Depends(get_request_pagination),
    price_service: "PriceService" = Depends(Provide[Container.price_service]),
    preco_de_less_than: Optional[float] = Query(None, description='Filtrar preços "de" menores que o valor informado'),
    preco_de_greater_than: Optional[float] = Query(
        None, description='Filtrar preços "de" maiores que o valor informado'
    ),
    preco_por_less_than: Optional[float] = Query(
        None, description='Filtrar preços "por" menores que o valor informado'
    ),
    preco_por_greater_than: Optional[float] = Query(
        None, description='Filtrar preços "por" maiores que o valor informado'
    ),
    sku: Optional[str] = Query(None, description="Filtrar por SKU específico"),
):

    logger.info(
        "Recuperando lista de precificações para seller_id: %s",
        seller_id,
        extra={"trace-id": "N/A"},
    )

    filters = {
        "de__lt": preco_de_less_than,
        "de__gt": preco_de_greater_than,
        "por__lt": preco_por_less_than,
        "por__gt": preco_por_greater_than,
        "sku": sku,
    }

    results = await price_service.get_filtered(paginator=paginator, filters=filters)

    return paginator.paginate(results=results)


# Busca precificação por "seller_id" e "sku"
@router.get(
    "/{sku}",
    response_model=PriceResponse,
    status_code=status.HTTP_200_OK,
    summary="Recuperar precificação por seller_id e sku",
    responses={404: NOT_FOUND_RESPONSE, 400: MISSING_HEADER_RESPONSE},
)
@inject
async def get_by_seller_id_and_sku(
    sku: str,
    price_service: "PriceService" = Depends(Provide[Container.price_service]),
    seller_id: str = Depends(get_required_seller_id),
):
    logger.info(
        "Recuperando precificação para seller_id: %s, sku: %s",
        seller_id,
        sku,
        extra={"trace-id": "N/A"},
    )

    return await price_service.get_by_seller_id_and_sku(seller_id=seller_id, sku=sku)


# Cria uma precificação
@router.post(
    "",
    response_model=PriceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar precificação",
    responses={400: BAD_REQUEST_RESPONSE},
)
@inject
async def create(
    price: PriceCreate,
    price_service: "PriceService" = Depends(Provide[Container.price_service]),
    seller_id: str = Depends(get_required_seller_id),
    user_info: UserAuthInfo = Depends(get_current_user),
):
    logger.info(
        "Criando precificação para seller_id: %s, sku: %s",
        seller_id,
        price.sku,
        extra={"preço": price, "trace-id": user_info.trace_id},
    )

    price_model = Price(**price.model_dump(), seller_id=seller_id)

    price_model.created_by = user_info.user
    price_model.updated_by = user_info.user

    logger.info(f"created_by: {price_model.created_by}, updated_by: {price_model.updated_by}")

    return await price_service.create(price_model)


# Atualiza uma precificação por "seller_id" e "sku"
@router.put(
    "/{sku}",
    response_model=PriceResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar precificação por seller_id e sku",
    responses={404: NOT_FOUND_RESPONSE, 400: BAD_REQUEST_RESPONSE},
)
@inject
async def replace(
    sku: str,
    price: PriceUpdate,
    price_service: "PriceService" = Depends(Provide[Container.price_service]),
    seller_id: str = Depends(get_required_seller_id),
    user_info: UserAuthInfo = Depends(get_current_user),
):
    logger.info(
        "Atualizando precificação para seller_id: %s, sku: %s",
        seller_id,
        sku,
        extra={"preço": price, "trace-id": user_info.trace_id},
    )

    price_model = Price(seller_id=seller_id, sku=sku, **price.model_dump())

    price_model.updated_by = user_info.user

    return await price_service.update(seller_id, sku, price_model)


# Atualiza parcialmente uma precificação por "seller_id" e "sku"
@router.patch(
    "/{sku}",
    response_model=PriceResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar parcialmente precificação por seller_id e sku",
    responses={404: NOT_FOUND_RESPONSE, 400: BAD_REQUEST_RESPONSE},
)
@inject
async def patch(
    sku: str,
    price_update_data: PricePatch,
    price_service: "PriceService" = Depends(Provide[Container.price_service]),
    seller_id: str = Depends(get_required_seller_id),
    user_info: UserAuthInfo = Depends(get_current_user),
):
    logger.info(
        "Atualizando parcialmente precificação para seller_id: %s, sku: %s",
        seller_id,
        sku,
        extra={"preço": price_update_data, "trace-id": user_info.trace_id},
    )

    return await price_service.patch(seller_id, sku, price_update_data, user_info)


# Deleta uma precificação por "seller_id" e "sku"
@router.delete(
    "/{sku}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir precificação por seller_id e sku",
    responses={404: NOT_FOUND_RESPONSE, 400: MISSING_HEADER_RESPONSE},
)
@inject
async def delete(
    sku: str,
    price_service: "PriceService" = Depends(Provide[Container.price_service]),
    seller_id: str = Depends(get_required_seller_id),
):
    logger.info(
        "Excluindo precificação para seller_id: %s, sku: %s",
        seller_id,
        sku,
    )

    await price_service.delete(seller_id, sku)


# Busca histórico de precificação por "seller_id" e "sku"
@router.get(
    "/historico/{sku}",
    response_model=PriceHistoryListResponse,
    status_code=status.HTTP_200_OK,
    summary="Recuperar histórico de precificação de um produto por seller_id e sku",
    responses={404: HISTORY_NOT_FOUND_RESPONSE, 400: MISSING_HEADER_RESPONSE},
)
@inject
async def get_history_by_seller_id_and_sku(
    sku: str,
    price_history_service: "PriceHistoryService" = Depends(Provide[Container.price_history_service]),
    seller_id: str = Depends(get_required_seller_id),
    paginator: Paginator = Depends(get_request_pagination),
):
    logger.info(
        "Recuperando histórico de precificação de um produto para seller_id: %s, sku: %s",
        seller_id,
        sku,
        extra={"trace-id": "N/A"},
    )

    return await price_history_service.get_by_seller_id_and_sku(seller_id=seller_id, sku=sku, paginator=paginator)


@router.post(
    "/{sku}/sugerir-preco",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Solicita sugestão de preço via IA",
    response_model=PriceSuggestionResponse,
    responses={
        400: MISSING_HEADER_RESPONSE,
    },
)
@inject
async def solicitar_sugestao_preco(
    sku: str,
    seller_id: str = Depends(get_required_seller_id),
    price_service: "PriceService" = Depends(Provide[Container.price_service]),
):
    logger.info(
        "Solicitando sugestão de preço por análise de histórico para seller_id: %s, sku: %s",
        seller_id,
        sku,
        extra={"trace-id": "N/A"},
    )

    return await price_service.request_price_suggestion(seller_id=seller_id, sku=sku)


# Consulta status/resultado da sugestão de preço
@router.get(
    "/sugerir-preco/status/{job_id}",
    summary="Consulta status da sugestão de preço via IA",
    responses={200: {"description": "Status ou resultado da sugestão"}},
    response_model=PriceSuggestionResponse,
)
@inject
async def status_sugestao_preco(
    job_id: str,
    price_service: "PriceService" = Depends(Provide[Container.price_service]),
    seller_id: str = Depends(get_required_seller_id),
):
    logger.info(
        "Verificando status da sugestão de preço por análise de histórico para job_id: %s",
        job_id,
        extra={"trace-id": "N/A"},
    )

    return await price_service.get_price_suggestion(job_id=job_id)
