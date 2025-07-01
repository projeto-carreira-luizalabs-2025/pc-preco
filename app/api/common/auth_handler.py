"""
'Camada' de segurança para a API
"""

from typing import TYPE_CHECKING, Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from app.api.common.injector import get_seller_id
from app.common.exceptions import ForbiddenException, UnauthorizedException
from app.container import Container
from app.integrations.auth.keycloak_adapter import OAuthException

from app.models.base import UserModel

if TYPE_CHECKING:
    from app.integrations.auth.keycloak_adapter import KeycloakAdapter


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8080/realms/marketplace/protocol/openid-connect/token")


class UserAuthInfo(BaseModel):
    """
    Dados do usuário autenticado.
    """

    # Quem é o usuário
    user: UserModel
    # O 'rastreador' da requisição.
    trace_id: str | None
    # Os sellers que o usuário pode operar.
    sellers: list[str]

    @staticmethod
    def to_sellers(sellers: str | None) -> list[str]:
        sellers = sellers.split(",") if sellers else []
        return sellers


@inject
async def do_auth(
    request: Request,
    token: Annotated[str, Depends(oauth2_scheme)],
    seller_id: str = Depends(get_seller_id),
    openid_adapter: "KeycloakAdapter" = Depends(Provide[Container.keycloak_adapter]),
) -> UserAuthInfo:
    """
    Responsável por fazer a autenticação com algum IDP OpenId.
    """

    try:
        info_token = await openid_adapter.validate_token(token)
    except OAuthException as exception:
        raise UnauthorizedException from exception

    user_info = UserAuthInfo(
        user=UserModel(name=info_token.get("sub"), server=info_token.get("iss")),
        trace_id=request.state.trace_id,
        sellers=UserAuthInfo.to_sellers(info_token.get("sellers")),
    )

    sellers = user_info.sellers

    if seller_id not in sellers:
        raise ForbiddenException([{"message": "não autorizado para trabalhar com este seller"}])

    request.state.user = user_info

    return user_info


async def get_current_user(request: Request) -> UserAuthInfo:
    """
    Obtém o usuário autenticado a partir do estado da requisição.
    """

    user = request.state.user

    return user
