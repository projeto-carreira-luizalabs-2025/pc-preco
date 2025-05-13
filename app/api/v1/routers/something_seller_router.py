from typing import TYPE_CHECKING

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from app.api.common.schemas import ListResponse, Paginator, UuidType, get_request_pagination
from app.container import Container

from ..schemas.something_schema import SomethingCreate, SomethingCreateResponse, SomethingResponse, SomethingUpdate
from . import SOMETHING_PREFIX

if TYPE_CHECKING:
    from app.services import SomethingService


router = APIRouter(prefix=SOMETHING_PREFIX, tags=["Algumas Coisas"])


@router.get(
    "",
    response_model=ListResponse[SomethingResponse],
    status_code=status.HTTP_200_OK,
)
@inject
async def get(
    name: str | None = None,
    paginator: Paginator = Depends(get_request_pagination),
    something_service: "SomethingService" = Depends(Provide[Container.something_service]),
):
    """
    Pesquisa pelos registros pelos filtros informados.

    - name: Filtra os registros que começam com o nome informado.
    """
    filters = {"name": name}
    results = await something_service.find(paginator, filters)

    return paginator.paginate(results=results)


@router.get(
    "/{something_id}",
    response_model=SomethingResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_by_id(
    something_id: int,
    something_service: "SomethingService" = Depends(Provide[Container.something_service]),
):
    """
    Pesquisa por alguma coisa com base em sua chave.
    """
    something = await something_service.find_by_id(something_id, can_raise_exception=True)
    return something.model_dump()


@router.post(
    "",
    response_model=SomethingCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create(
    something: SomethingCreate, something_service: "SomethingService" = Depends(Provide[Container.something_service])
) -> SomethingCreateResponse:
    """
    Salva alguma coisa na base, retornando a chave `identity`.
    """
    return await something_service.create(something)


@router.patch(
    "/{something_id}",
    response_model=SomethingResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def update_by_id(
    something_id: int,
    something: SomethingUpdate,
    something_service: "SomethingService" = Depends(Provide[Container.something_service]),
):
    return await something_service.update(something_id, something)


@router.delete("/{something_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete(
    something_id: UuidType, something_service: "SomethingService" = Depends(Provide[Container.something_service])
):
    await something_service.delete_by_id(something_id)
