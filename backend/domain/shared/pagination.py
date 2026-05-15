from enum import StrEnum
from typing import Generic, TypeVar

from pydantic import Field

from domain.entities import ValueObject

T = TypeVar("T")


class SortDirection(StrEnum):
    ASC = "asc"
    DESC = "desc"


class SortSpec(ValueObject):
    field: str
    direction: SortDirection


class PageRequest(ValueObject):
    limit: int = Field(ge=1, le=200)
    offset: int = Field(ge=0)
    sort: SortSpec


class Page(ValueObject, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int
