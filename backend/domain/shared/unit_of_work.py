from abc import ABC, abstractmethod
from typing import Self


class AbstractUnitOfWork(ABC):
    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        if not self.is_committed:
            await self.rollback()

    @property
    @abstractmethod
    def is_committed(self) -> bool: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
