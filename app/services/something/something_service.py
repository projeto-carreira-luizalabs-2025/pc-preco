from ...models import Something
from ...repositories import SomethingRepository
from ..base import CrudService
from .something_exceptions import SomethingAlreadyExistsException


class SomethingService(CrudService[Something, int]):
    def __init__(self, repository: SomethingRepository):
        super().__init__(repository)

    async def create(self, something: Something) -> Something:
        # Minhas regras para cadastrar `something`

        # A chave `identity` é única
        another_identity = await self.repository.find_by_id(something.identify)
        if another_identity is not None:
            raise SomethingAlreadyExistsException()

        resp = await super().create(something)
        return resp

    async def find_by_name(self, name: str) -> Something:
        """
        Busca um Something pelo nome.
        """
        return await self.repository.find_by_name(name=name)
