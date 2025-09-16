from typing import Generic, TypeVar

T = TypeVar("T")


class PaginatedResult(Generic[T]):
    def __init__(self, items: list[T], total: int, page: int, per_page: int):
        self.items = items
        self.total = total
        self.page = page
        self.per_page = per_page
        self.pages = (total + per_page - 1) // per_page
        self.has_prev = page > 1
        self.has_next = page < self.pages
        self.prev_num = page - 1 if self.has_prev else None
        self.next_num = page + 1 if self.has_next else None

    @property
    def first_item(self) -> int:
        if self.total == 0:
            return 0
        return ((self.page - 1) * self.per_page) + 1

    @property
    def last_item(self) -> int:
        if self.total == 0:
            return 0
        return min(self.page * self.per_page, self.total)

    def iter_pages(
        self,
        left_edge: int = 2,
        right_edge: int = 2,
        left_current: int = 2,
        right_current: int = 2,
    ):
        last = self.pages
        if last <= 0:
            return

        for num in range(1, min(left_edge + 1, last + 1)):
            yield num

        if left_edge + 1 < self.page - left_current:
            yield None

        start = max(left_edge + 1, self.page - left_current)
        end = min(last + 1, self.page + right_current + 1)
        for num in range(start, end):
            yield num

        if self.page + right_current < last - right_edge:
            yield None

        start = max(self.page + right_current + 1, last - right_edge + 1)
        for num in range(start, last + 1):
            yield num
