import math
from fastapi import Query


class Pagination:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(20, ge=1, le=100, description="Items per page"),
    ):
        self.page = page
        self.size = size
        self.offset = (page - 1) * size

    def paginate(self, total: int) -> dict:
        pages = math.ceil(total / self.size) if total > 0 else 0
        return {
            "total": total,
            "page": self.page,
            "size": self.size,
            "pages": pages,
        }
