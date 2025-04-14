from pydantic import BaseModel


class CampaignStats(BaseModel):
    impressions_count: int
    clicks_count: int
    conversion: float
    spent_impressions: float
    spent_clicks: float
    spent_total: float


class CampaignDailyStats(CampaignStats):
    date: int
