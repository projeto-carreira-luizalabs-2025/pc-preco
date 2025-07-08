from pydantic import Field

from .app import AppSettings


class WorkerSettings(AppSettings):
    enabled_workers: set[str] = Field(
        default={"customer"},
        title="Workers que devem ser inicializados",
    )

    ia_api_url: str = Field(..., description="URL da API da IA")
    ia_model: str = Field(..., description="Modelo da IA")


worker_settings = WorkerSettings()
