from typing import Generic, TypeVar

from fastapi import HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

from domain.shared.pagination import PageRequest, SortDirection, SortSpec

T = TypeVar("T")


class PageResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(extra="forbid")

    items: list[T]
    total: int
    limit: int
    offset: int


class PaginationParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    limit: int = Field(20, ge=1, le=200)
    offset: int = Field(0, ge=0)
    sort: str = Field("id")
    direction: SortDirection = SortDirection.ASC

    def to_page_request(self, *, allowed_fields: frozenset[str]) -> PageRequest:
        if self.sort not in allowed_fields:
            raise HTTPException(
                status_code=400,
                detail=f"sort must be one of {sorted(allowed_fields)}",
            )
        return PageRequest(
            limit=self.limit,
            offset=self.offset,
            sort=SortSpec(field=self.sort, direction=self.direction),
        )


def pagination_params(
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort: str = Query("id"),
    direction: SortDirection = Query(SortDirection.ASC),
) -> PaginationParams:
    return PaginationParams(limit=limit, offset=offset, sort=sort, direction=direction)
