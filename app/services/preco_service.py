from ..models import Something
from ..repositories import PrecoRepository
from .base import CrudService


class PrecoService(CrudService[Something, int]):
    def __init__(self, repository: PrecoRepository):
        super().__init__(repository)

    async def find_by_name(self, name: str) -> Something:
        """
        Busca um Something pelo nome.
        """
        return await self.repository.find_by_name(name=name)
