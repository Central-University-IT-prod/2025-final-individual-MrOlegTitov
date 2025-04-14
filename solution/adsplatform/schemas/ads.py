from uuid import UUID

from pydantic import BaseModel


class Ad(BaseModel):
    ad_id: UUID
    ad_title: str
    ad_text: str
    advertiser_id: UUID
