"""
Central para executar os workers.

No modelo atual somente temos um que trabalha com a tarefa de eventos de
criação de tickets (create_ticket_task)
"""

import asyncio
import logging
import signal
import sys
import time

from dependency_injector.wiring import Provide

from ..settings.worker import WorkerSettings
from .container_event_worker import WorkerContainer

from .tasks.create_alert_task import CreateAlertTask

logger = logging.getLogger(__name__)


class WorkerMain:
    """
    Classe principal para executar os workers
    """

    def __init__(self):
        self.container = WorkerContainer()
        self.tasks = []
        self._current_event_loop = None

    def init_container(self):
        settings = WorkerSettings()
        self.container.config.from_pydantic(settings)
        self.container.wire([__name__])

    @staticmethod
    def get_tasks(create_alert_task: CreateAlertTask = Provide[WorkerContainer.create_alert_task]) -> list:
        tasks = (create_alert_task,)
        return tasks

    def init(self):
        # XXX Configurando o logger aqui mesmo
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s -   %(message)s")
        logging.getLogger("pika").setLevel(logging.WARNING)
        self.init_container()
        self._current_event_loop = asyncio.get_running_loop()

        def handler_sig(signum, frame):
            """
            Função que será executada quando o signal SIGINT for recebido
            """
            logger.info("INTerrompendo workers")
            try:
                for t in self.tasks:
                    self._current_event_loop.create_task(t.close())
                    time.sleep(0.5)
            finally:
                self.tasks = []
            sys.exit(0)

        signal.signal(signal.SIGINT, handler_sig)

    async def run(self):
        """
        Inicia o container e executa as tasks.
        """
        self.init()

        self.tasks = self.get_tasks()

        await asyncio.gather(*(task.run() for task in self.tasks))


if __name__ == "__main__":
    asyncio.run(WorkerMain().run())
