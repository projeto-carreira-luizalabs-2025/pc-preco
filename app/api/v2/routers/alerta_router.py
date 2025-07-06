from typing import TYPE_CHECKING, Optional
from fastapi import Query
import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from app.api.common.auth_handler import do_auth
from app.api.common.dependencies import get_required_seller_id
from app.api.common.responses.price_responses import (
    UNPROCESSABLE_ENTITY_RESPONSE,
)
from app.api.common.schemas import ListResponse, Paginator, get_request_pagination
from app.api.v2.schemas.alerta_schema import AlertResponse
from app.container import Container

from . import ALERTA_PREFIX

if TYPE_CHECKING:
    from app.services import AlertService


router = APIRouter(prefix=ALERTA_PREFIX, tags=["Alertas"], dependencies=[Depends(do_auth)])

logger = logging.getLogger(__name__)


# Recupera lista de alertas
@router.get(
    "",
    response_model=ListResponse[AlertResponse],
    status_code=status.HTTP_200_OK,
    summary="Recuperar lista de alertas",
    responses={422: UNPROCESSABLE_ENTITY_RESPONSE},
)
@inject
async def get(
    seller_id: str = Depends(get_required_seller_id),
    paginator: Paginator = Depends(get_request_pagination),
    alert_service: "AlertService" = Depends(Provide[Container.alert_service]),
    sku: Optional[str] = Query(None, description="Filtrar por SKU específico"),
):
    logger.info(
        "Recuperando lista de alertas para seller_id: %s",
        seller_id,
        extra={"trace-id": "N/A"},
    )

    filters = {
        "sku": sku,
    }

    results = await alert_service.get_alerts(paginator=paginator, filters=filters)

    return paginator.paginate(results=results)
