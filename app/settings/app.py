from pydantic import Field, HttpUrl, PostgresDsn, RedisDsn

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

    pc_logging_level: str = Field("DEBUG", description="Nível do logging")
    pc_logging_env: str = Field("prod", description="Ambiente do logging (prod ou dev ou test)")

    app_redis_url: RedisDsn = Field(..., title="URL para o Redis")

    app_queue_url: str = Field(..., title="URL para o RabbitMQ")
    app_alert_queue_name: str = Field(..., title="Nome da fila de alertas no RabbitMQ")
    app_price_suggestion_queue_name: str = Field(..., title="Nome da fila de sugestões de preço no RabbitMQ")


settings = AppSettings()
