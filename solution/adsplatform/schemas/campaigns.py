from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class TargetingGender(str, Enum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    ALL = 'ALL'


class CampaignTargeting(BaseModel):
    gender: TargetingGender | None = None
    age_from: int | None = Field(default=None, ge=0)
    age_to: int | None = Field(default=None, ge=0)
    location: str | None = None

    @field_validator('age_from')
    def validate_age_from(cls, v: int | None, info: ValidationInfo) -> int | None:
        age_to = info.data.get('age_to')
        if v is not None and age_to is not None and v > age_to:
            raise ValueError('age_from cannot be greater than age_to')

        return v

    @field_validator('age_to')
    def validate_age_to(cls, v: int | None, info: ValidationInfo) -> int | None:
        age_from = info.data.get('age_from')
        if v is not None and age_from is not None and v < age_from:
            raise ValueError('age_to cannot be less than age_from')

        return v


class CampaignEdit(BaseModel):
    impressions_limit: int | None = Field(default=None, ge=0)
    clicks_limit: int | None = Field(default=None, ge=0)
    cost_per_impression: float | None = Field(default=None, gt=0)
    cost_per_click: float | None = Field(default=None, gt=0)
    start_date: int | None = Field(default=None, ge=0)
    end_date: int | None = Field(default=None, ge=0)
    ad_title: str | None = None
    ad_text: str | None = None
    ad_image: str | None = None
    targeting: CampaignTargeting | None = None

    @field_validator('start_date')
    def validate_start_date(cls, v: int | None, info: ValidationInfo) -> int | None:
        end_date = info.data.get('end_date')
        if end_date is not None and v is not None and v > end_date:
            raise ValueError('start_date cannot be greater than end_date')

        return v

    @field_validator('end_date')
    def validate_end_date(cls, v: int | None, info: ValidationInfo) -> int | None:
        start_date = info.data.get('start_date')
        if start_date is not None and v is not None and v < start_date:
            raise ValueError('end_date cannot be less than start_date')

        return v

    @field_validator('clicks_limit')
    def validate_clicks_limit(cls, v: int | None, info: ValidationInfo) -> int | None:
        impression_limit = info.data.get('impressions_limit')
        if impression_limit is not None and v is not None and v > impression_limit:
            raise ValueError('clicks_limit cannot be greater than impressions_limit')

        return v


class CampaignIn(CampaignEdit):
    impressions_limit: int = Field(ge=0)
    clicks_limit: int = Field(ge=0)
    cost_per_impression: float = Field(gt=0)
    cost_per_click: float = Field(gt=0)
    ad_title: str
    ad_text: str
    start_date: int = Field(ge=0)
    end_date: int = Field(ge=0)


class Campaign(CampaignIn):
    campaign_id: UUID
    advertiser_id: UUID
