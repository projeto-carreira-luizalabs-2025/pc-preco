from typing import TYPE_CHECKING

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Path, status

from app.api.common.schemas import ListResponse, Paginator, get_request_pagination
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
    description="Recupera uma lista paginada de precificações com suporte a ordenação e filtragem.",
    response_description="Lista paginada de precificações com metadados de navegação.",
)
@inject
async def get(
    paginator: Paginator = Depends(get_request_pagination),
    preco_service: "PrecoService" = Depends(Provide[Container.preco_service]),
):
    """
    Recupera uma lista paginada de precificações.

    Esta operação retorna todas as precificações cadastradas no sistema, com suporte a paginação,
    ordenação e filtragem. Os resultados são ordenados por data de criação por padrão.
    """
    results = await preco_service.find(paginator=paginator, filters={})
    return paginator.paginate(results=results)


@router.get(
    "/{seller_id}/{sku}",
    response_model=PrecoResponse,
    status_code=status.HTTP_200_OK,
    summary="Recuperar precificação por seller_id e sku",
    description="Busca uma precificação específica utilizando o identificador do seller e o SKU do produto.",
    response_description="Detalhes da precificação encontrada.",
)
@inject
async def get_by_seller_id_and_sku(
    seller_id: str = Path(..., description="Identificador único do seller", examples=["seller123"]),
    sku: str = Path(..., description="Código SKU do produto", examples=["SKU001"]),
    preco_service: "PrecoService" = Depends(Provide[Container.preco_service]),
):
    """
    Busca precificação por "seller_id" e "sku".

    Esta operação retorna uma precificação específica com base no identificador do seller e no SKU do produto.
    Se a precificação não for encontrada, retorna um erro 404.
    """
    return await preco_service.find_by_seller_id_and_sku(seller_id=seller_id, sku=sku)


@router.post(
    "",
    response_model=PrecoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar precificação",
    description="Cria uma nova precificação para um produto específico de um seller.",
    response_description="Detalhes da precificação criada com sucesso.",
)
@inject
async def create(
    preco: PrecoCreate = Body(
        ...,
        description="Dados da precificação a ser criada",
        json_schema_extra={  # Correção: Usar json_schema_extra
            "examples": {
                "default": {
                    "summary": "Exemplo de criação de preço",
                    "value": {
                        "seller_id": "seller123",
                        "sku": "SKU001",
                        "preco_de": 10000,
                        "preco_por": 8500,
                    },
                }
            }
        },
    ),
    preco_service: "PrecoService" = Depends(Provide[Container.preco_service]),
):
    """
    Cria uma precificação para um produto.

    Esta operação permite cadastrar uma nova precificação para um produto específico de um seller.
    Os valores de preço devem ser informados em centavos (ex: R$ 100,00 = 10000).
    """
    return await preco_service.create_preco(preco)


@router.patch(
    "/{seller_id}/{sku}",
    response_model=PrecoResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar precificação",
    description="Atualiza os preços de uma precificação existente identificada pelo seller_id e sku.",
    response_description="Detalhes da precificação atualizada com sucesso.",
)
@inject
async def update_by_id(
    seller_id: str = Path(..., description="Identificador único do seller", examples=["seller123"]),
    sku: str = Path(..., description="Código SKU do produto", examples=["SKU001"]),
    preco: PrecoUpdate = Body(
        ...,
        description="Dados da precificação a serem atualizados",
        json_schema_extra={
            "examples": {
                "default": {
                    "summary": "Exemplo de atualização de preço",
                    "value": {"preco_de": 12000, "preco_por": 9500},
                }
            }
        },
    ),
    preco_service: "PrecoService" = Depends(Provide[Container.preco_service]),
):
    """
    Atualiza uma precificação existente.

    Esta operação permite atualizar os preços de uma precificação existente identificada pelo seller_id e sku.
    Apenas os campos preco_de e preco_por podem ser atualizados.
    Os valores de preço devem ser informados em centavos (ex: R$ 100,00 = 10000).
    """
    return await preco_service.update_preco(seller_id, sku, preco)


@router.delete(
    "/{seller_id}/{sku}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir precificação por seller_id e sku",
    description="Exclui uma precificação existente identificada pelo seller_id e sku.",
    response_description="Operação realizada com sucesso, sem conteúdo de retorno.",
)
@inject
async def delete_by_seller_id_and_sku(
    seller_id: str = Path(..., description="Identificador único do seller", examples=["seller123"]),
    sku: str = Path(..., description="Código SKU do produto", examples=["SKU001"]),
    preco_service: "PrecoService" = Depends(Provide[Container.preco_service]),
):
    """
    Exclui uma precificação pelo seller_id e sku.

    Esta operação remove permanentemente uma precificação do sistema utilizando o identificador do seller
    e o SKU do produto.
    """
    await preco_service.delete_by_seller_id_and_sku(seller_id, sku)
