from typing import TYPE_CHECKING

from dependency_injector.wiring import Provide, inject
from fastapi import HTTPException, APIRouter, Depends, status

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
)
@inject
async def get(
    paginator: Paginator = Depends(get_request_pagination),
    preco_service: "PrecoService" = Depends(Provide[Container.preco_service]),
):
    results = await preco_service.find(paginator=paginator, filters={})

    return paginator.paginate(results=results)


@router.get(
    "/{preco_id}",
    response_model=PrecoResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_by_id(
    preco_id: int,
    preco_service: "PrecoService" = Depends(Provide[Container.preco_service]),
):
    return await preco_service.find_by_id(preco_id)


@router.post(
    "",
    response_model=PrecoResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create(preco: PrecoCreate, preco_service: "PrecoService" = Depends(Provide[Container.preco_service])):
    # Verificar se já há um preço de produto (seller_id + sku) cadastrado
    preco_encontrado = await preco_service.find_by_seller_id_and_sku(seller_id=preco.seller_id, sku=preco.sku)

    if preco_encontrado:
        raise HTTPException(
            status_code=409, detail="Preço para produto já cadastrado."
        )  # Melhorar aqui depois, no response body não está retornando a mensagem

    # Verificar se há valores positivos para os preços
    if preco.preco_de <= 0:
        raise HTTPException(status_code=422, detail="'preco_de' deve ser maior que zero.")
    if preco.preco_por <= 0:
        raise HTTPException(status_code=422, detail="'preco_por' deve ser maior que zero.")

    return await preco_service.create(preco)


@router.patch(
    "/{preco_id}",
    response_model=PrecoResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def update_by_id(
    preco_id: int,
    preco: PrecoUpdate,
    preco_service: "PrecoService" = Depends(Provide[Container.preco_service]),
):
    return await preco_service.update(preco_id, preco)


@router.delete("/{preco_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete(preco_id: UuidType, preco_service: "PrecoService" = Depends(Provide[Container.preco_service])):
    await preco_service.delete_by_id(preco_id)
