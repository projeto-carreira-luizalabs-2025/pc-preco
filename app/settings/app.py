from pydantic import Field, PostgresDsn, HttpUrl

from .base import BaseSettings


class AppSettings(BaseSettings):
    version: str = Field("0.5.0", description="Versão da aplicação")

    app_name: str = Field(
        default="PC Preço",
        title="Nome da aplicação",
        description="Microsserviço responsável por gerenciar os valores do marketplace",
    )

    memory_min: int = Field(default=64, title="Limite mínimo de memória disponível em MB")
    disk_usage_max: int = Field(default=80, title="Limite máximo de 80% de uso de disco")

    app_db_url: PostgresDsn = Field(..., title="URI para o banco Postgresql")

    app_openid_wellknown: HttpUrl = Field(..., title="URL para well known de um openid")


settings = AppSettings()
