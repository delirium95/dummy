from abc import abstractmethod

from domain.post.interfaces import PostRepository
from domain.shared.unit_of_work import AbstractUnitOfWork
from domain.user.interfaces import UserRepository


class UnitOfWork(AbstractUnitOfWork):
    @property
    @abstractmethod
    def user_repository(self) -> UserRepository: ...

    @property
    @abstractmethod
    def post_repository(self) -> PostRepository: ...
