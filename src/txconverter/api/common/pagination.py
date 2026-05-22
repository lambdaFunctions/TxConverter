from dataclasses import dataclass
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")

MAX_PAGE_SIZE = 100


@dataclass(frozen=True)
class PageParams:
    page: int = 1
    page_size: int = 20

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError(f"page must be >= 1, got {self.page}")
        if not (1 <= self.page_size <= MAX_PAGE_SIZE):
            raise ValueError(
                f"page_size must be between 1 and {MAX_PAGE_SIZE}, got {self.page_size}"
            )


class PaginatedResult(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int

    @classmethod
    def build(
        cls, items: list[T], total: int, params: PageParams
    ) -> "PaginatedResult[T]":
        return cls(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=max(1, -(-total // params.page_size)),
        )


def paginate(items: list[T], params: PageParams) -> PaginatedResult[T]:
    """In-memory pagination helper for repos that already hold a bounded list."""
    total = len(items)
    offset = (params.page - 1) * params.page_size
    return PaginatedResult.build(
        items[offset : offset + params.page_size], total, params
    )
