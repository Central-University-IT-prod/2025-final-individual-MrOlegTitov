from uuid import UUID

from pydantic import BaseModel, Field


class Advertiser(BaseModel):
    advertiser_id: UUID
    name: str


class MLScore(BaseModel):
    client_id: UUID
    advertiser_id: UUID
    score: int = Field(ge=0)
