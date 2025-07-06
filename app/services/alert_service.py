from app.api.common.schemas import Paginator
from app.models.alert_filter_model import AlertFilter
from app.models.alert_model import Alert
from app.repositories.alert_repository import AlertRepository

from .base import CrudService


class AlertService(CrudService[Alert]):

    repository: AlertRepository

    def __init__(self, alert_repository: AlertRepository):
        super().__init__(alert_repository)

    async def create_alert(self, alert_data) -> Alert:
        """
        Cria um novo alerta com os dados fornecidos.
        :param alert_data: Dados do alerta a ser criado.
        :return: Instância do alerta criado.
        """
        return await self.create(alert_data)

    async def get_alerts(self, paginator=Paginator, filters=dict) -> list[Alert]:
        """
        Busca alertas com base nos filtros fornecidos e retorna uma lista paginada.
        :param paginator: Paginator para paginação dos resultados.
        :param filters: Filtros para busca de alertas.
        :return: Lista paginada de alertas.
        """
        current_filters = {key: value for key, value in filters.items() if value is not None}

        filter_model = AlertFilter(**current_filters)

        return await self.find(filters=filter_model, paginator=paginator)
