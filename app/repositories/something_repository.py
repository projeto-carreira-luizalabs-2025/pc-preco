from uuid import UUID

from ..models import Something
from .base import AsyncMemoryRepository


class SomethingRepository(AsyncMemoryRepository[Something, UUID]):

    def __init__(self):
        super().__init__("identify", Something)

    async def find_by_name(self, name: str) -> Something:
        """
        Busca um alguma coisa pelo nome.
        """
        result = next((s for s in self.memory if s["name"] == name), None)
        return result


__all__ = ["SomethingRepository"]
