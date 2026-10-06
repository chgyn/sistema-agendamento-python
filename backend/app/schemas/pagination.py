from typing import Generic, TypeVar
import math
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")

DEFAULT_PAGE_SIZE: int = 10
MAX_PAGE_SIZE: int = 100


class PaginatedResponse(BaseModel, Generic[T]):
    """Contrato genérico padronizado de resposta paginada para todas as listagens."""

    items: list[T] = Field(description="Lista de itens da página solicitada")
    total: int = Field(ge=0, description="Total geral de registros encontrados")
    page: int = Field(ge=1, description="Número da página atual (1-based)")
    page_size: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Quantidade de itens por página")
    total_pages: int = Field(ge=0, description="Quantidade total de páginas calculadas")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def create(cls, items: list[T], total: int, page: int, page_size: int) -> "PaginatedResponse[T]":
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
