from pydantic import BaseModel


class TextModerationOut(BaseModel):
    is_safe: bool
    unsafe_category: str | None = None


class AdTextGenerationIn(BaseModel):
    ad_title: str
    advertiser_name: str
