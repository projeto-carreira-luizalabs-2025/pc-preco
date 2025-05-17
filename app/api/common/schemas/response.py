from typing import Generic, Literal, Sequence, TypeVar

from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.common.error_codes import ErrorInfo
from app.settings import api_settings

from .navigation_links import NavigationLinks

T = TypeVar("T")

PAGE_MAX_LIMIT = api_settings.pagination.max_limit


class PageResponse(BaseModel):
    """
    Metadados de paginação incluídos nas respostas de listagem.

    Esta classe contém informações sobre a paginação atual, incluindo
    o limite de itens por página, o offset utilizado, a quantidade de itens
    retornados e o limite máximo permitido.
    """
    limit: int | None = Field(
        default=50,
        ge=1,
        le=PAGE_MAX_LIMIT,
        description="Quantidade de registros solicitados por página",
        example=50
    )
    offset: int | None = Field(
        default=0,
        ge=0,
        description="Posição inicial a partir da qual os registros foram retornados",
        example=0
    )
    count: int | None = Field(
        default=0, 
        description="Quantidade total de registros retornados nessa página",
        example=25
    )
    max_limit: int | None = Field(
        default=PAGE_MAX_LIMIT,
        description="Valor máximo permitido para o parâmetro limit",
        example=100
    )


class Page(BaseModel):
    current: int | None = Field(1, description="Current page")
    previous: int | None = Field(None, description="Previous page")
    next: int | None = Field(None, description="Next page")
    size: int = Field(20, description="Number of items per page")
    pages: int = Field(..., description="Total of pages")


class ListMeta(BaseModel):
    """
    Metadados incluídos nas respostas de listagem.

    Esta classe agrupa os metadados de paginação e navegação que são
    incluídos nas respostas de listagem.
    """
    page: PageResponse | None = Field(
        default=None, 
        description="Metadados de paginação"
    )
    links: NavigationLinks | None = Field(
        default=None, 
        description="Links de navegação entre páginas"
    )


class ListResponse(BaseModel, Generic[T]):
    """
    Estrutura padrão para respostas de listagem da API.

    Esta estrutura é utilizada para todas as respostas de listagem da API,
    fornecendo uma estrutura consistente com metadados de paginação e navegação,
    além dos resultados propriamente ditos.
    """
    meta: ListMeta | None = Field(
        None, 
        description="Metadados da resposta, incluindo paginação e links de navegação"
    )
    results: Sequence[T] | None = Field(
        None, 
        description="Lista de resultados retornados"
    )


type ErrorLocation = Literal["query", "path", "body", "header"]  # type: ignore[valid-type]


class ErrorDetail(BaseModel):
    """
    Detalhes específicos de um erro.

    Contém informações detalhadas sobre um erro específico, incluindo a mensagem,
    localização, identificador, campo relacionado e contexto adicional.
    """
    message: str = Field(..., description="Descrição detalhada do erro")
    location: ErrorLocation | None = Field(None, description="Localização do erro (query, path, body, header)")
    slug: str | None = Field(None, description="Identificador único do erro")
    field: str | None = Field(None, description="Nome do campo que gerou o erro")
    ctx: dict | None = Field(None, description="Contexto adicional do erro")


class ErrorResponse(BaseModel):
    """
    Estrutura padrão para respostas de erro da API.

    Esta estrutura é utilizada para todas as respostas de erro da API,
    fornecendo informações consistentes sobre o erro ocorrido.
    """
    slug: str = Field(..., description="Identificador único do erro")
    message: str = Field(..., description="Mensagem geral do erro")
    details: None | list[ErrorDetail] = Field(..., description="Lista de detalhes específicos do erro")


class FileBinaryResponse(Response):
    media_type = "binary/octet-stream"


def get_list_response(
    page: PageResponse,
    links: NavigationLinks,
    results: Sequence[BaseModel] | None = None,
) -> ListResponse:
    meta_kwargs: dict[str, PageResponse | NavigationLinks] = {
        "page": page,
        "links": links,
    }
    kwargs: dict[str, Sequence[BaseModel] | ListMeta | None] = {
        "results": results,
        "meta": ListMeta(**meta_kwargs),
    }

    return ListResponse(**kwargs)


def get_error_response(error: ErrorInfo, details: list[ErrorDetail] | None = None) -> ErrorResponse:
    return ErrorResponse(slug=error.slug, message=error.message, details=details)
