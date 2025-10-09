from typing import TypedDict

from gestaolegal.common.pagination_result import PaginatedResult

__all__ = ["PageParams", "PaginatedResult"]


class PageParams(TypedDict):
    page: int
    per_page: int
