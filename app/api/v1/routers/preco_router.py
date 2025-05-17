from typing import TYPE_CHECKING

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from app.api.common.schemas import ListResponse, Paginator, UuidType, get_request_pagination
from app.container import Container

from ..schemas.preco_schema import PrecoCreate, PrecoResponse, PrecoUpdate
from . import PRECO_PREFIX

if TYPE_CHECKING:
    from app.services import PrecoService


router = APIRouter(prefix=PRECO_PREFIX, tags=["Preços"])


@router.get(
    "",
    response_model=ListResponse[PrecoResponse],
    status_code=status.HTTP_200_OK,
    summary="Recuperar lista de precificações",
)
@inject
async def get(
    paginator: Paginator = Depends(get_request_pagination),
    preco_service: "PrecoService" = Depends(Provide[Container.preco_service]),
):
    """
    Recupera uma lista paginada de precificações.
    """
    results = await preco_service.find(paginator=paginator, filters={})
    return paginator.paginate(results=results)


@router.get(
    "/{seller_id}/{sku}",
    response_model=PrecoResponse,
    status_code=status.HTTP_200_OK,
    summary="Recuperar precificação por seller_id e sku",
)
@inject
async def get_by_seller_id_and_sku(
    seller_id: str,
    sku: str,
    preco_service: "PrecoService" = Depends(Provide[Container.preco_service]),
):
    """
    Busca precificação por "seller_id" e "sku".
    """
    return await preco_service.find_by_seller_id_and_sku(seller_id=seller_id, sku=sku)


@router.post(
    "",
    response_model=PrecoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar precificação",
)
@inject
async def create(
    preco: PrecoCreate, 
    preco_service: "PrecoService" = Depends(Provide[Container.preco_service])
):
    """
    Cria uma precificação para um produto.
    """
    return await preco_service.create_preco(preco)


@router.patch(
    "/{seller_id}/{sku}",
    response_model=PrecoResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar precificação",
)
@inject
async def update_by_id(
    seller_id: str,
    sku: str,
    preco: PrecoUpdate,
    preco_service: "PrecoService" = Depends(Provide[Container.preco_service]),
):
    """
    Atualiza uma precificação existente.
    """
    return await preco_service.update_preco(seller_id, sku, preco)


@router.delete("/{preco_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete(
    preco_id: UuidType, 
    preco_service: "PrecoService" = Depends(Provide[Container.preco_service])
):
    """
    Exclui uma precificação pelo ID.
    """
    await preco_service.delete_by_id(preco_id)


@router.delete(
    "/{seller_id}/{sku}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir precificação por seller_id e sku",
)
@inject
async def delete_by_seller_id_and_sku(
    seller_id: str,
    sku: str,
    preco_service: "PrecoService" = Depends(Provide[Container.preco_service])
):
    """
    Exclui uma precificação pelo seller_id e sku.
    """
    await preco_service.delete_by_seller_id_and_sku(seller_id, sku)
