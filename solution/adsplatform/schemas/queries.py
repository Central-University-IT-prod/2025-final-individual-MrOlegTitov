from pydantic import BaseModel, Field


class PaginationQuery(BaseModel):
    size: int | None = Field(default=None, ge=0)
    page: int | None = Field(default=0, ge=0)
