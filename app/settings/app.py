from pydantic import Field

from .base import BaseSettings


class AppSettings(BaseSettings):
    version: str = Field("0.2.1", description="Versão da aplicação")

    app_name: str = Field(default="PC Boleirplate", title="Nome da aplicação")

    memory_min: int = Field(default=64, title="Limite mínimo de memória disponível em MB")
    disk_usage_max: int = Field(default=80, title="Limite máximo de 80% de uso de disco")


settings = AppSettings()
