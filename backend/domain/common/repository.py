from abc import ABC, abstractmethod

from domain.error_messages import OBJECT_WAS_NOT_FOUND
from domain.errors import NotFoundError


class AbstractRepository[Identity_T, Aggregate_T](ABC):
    @abstractmethod
    async def add(self, obj: Aggregate_T, /) -> Aggregate_T:
        """Persist a new aggregate, returning the persisted form with assigned id."""

    @abstractmethod
    async def get(self, id_: Identity_T, /) -> Aggregate_T | None:
        """Return aggregate by id, or None if it does not exist."""

    @abstractmethod
    async def delete(self, id_: Identity_T, /) -> None:
        """Remove aggregate by id.

        Raises:
            NotFoundError: if no aggregate with the given id exists.
        """

    async def get_or_raise(self, id_: Identity_T, /) -> Aggregate_T:
        obj = await self.get(id_)
        if obj is None:
            raise NotFoundError(OBJECT_WAS_NOT_FOUND)
        return obj
