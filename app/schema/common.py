"""
common schema — pagination.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """پاسخ استاندارد موفق."""

    success: bool = True
    data: T


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict | None = None


class ErrorResponse(BaseModel):
    """پاسخ استاندارد خطا."""

    success: bool = False
    error: ErrorDetail


class PaginationParams(BaseModel):
    """پارامترهای صفحه‌بندی."""

    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PageMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class Page(BaseModel, Generic[T]):
    """پاسخ لیست صفحه‌بندی‌شده."""

    items: list[T]
    meta: PageMeta
