import math
from . import api_config, redis_client
from ..config import app_config
from ..db import init_db
from adsplatform.db.models import Advertisers, Clients, Campaigns, CampaignsTargeting
from ..schemas.ads import Ad
from ..schemas.advertisers import Advertiser
from ..schemas.campaigns import Campaign, CampaignTargeting
from ..schemas.clients import Client
from ..schemas.statistics import CampaignStats, CampaignDailyStats
from contextlib import asynccontextmanager

from fastapi import FastAPI

AD_RANDOM_CHANCE = 40
AD_MIN_IMPRESSIONS = 50
USER_MIN_IMPRESSIONS = 50
IMPRESSIONS_THRESHOLD = 0.85
CLICKS_THRESHOLD = 0.92
ML_SCORE_LOG_MULT = 15
ML_SCORE_DEFAULT = 0


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db(
        username=app_config.postgres_user,
        password=app_config.postgres_password,
        db_name=app_config.postgres_db,
    )
    if await redis_client.get('current_date') is None:
        await redis_client.set('current_date', api_config.start_date)
    yield


def serialize_client(client: Clients) -> Client:
    return Client(
        client_id=client.id,
        login=client.login,
        age=client.age,
        location=client.location,
        gender=client.gender,
    )


def serialize_advertiser(advertiser: Advertisers) -> Advertiser:
    return Advertiser(
        advertiser_id=advertiser.id,
        name=advertiser.name,
    )


async def serialize_campaign(campaign: Campaigns) -> Campaign:
    advertiser: Advertisers = await campaign.advertiser
    targeting: CampaignsTargeting | None = await campaign.targeting

    return Campaign(
        campaign_id=campaign.id,
        advertiser_id=advertiser.id,
        impressions_limit=campaign.impressions_limit,
        clicks_limit=campaign.clicks_limit,
        cost_per_impression=campaign.cost_per_impression,
        cost_per_click=campaign.cost_per_click,
        ad_title=campaign.ad_title,
        ad_text=campaign.ad_text,
        ad_image=campaign.ad_image,
        start_date=campaign.start_date,
        end_date=campaign.end_date,
        targeting=CampaignTargeting(
            gender=targeting.gender,
            age_from=targeting.age_from,
            age_to=targeting.age_to,
            location=targeting.location,
        )
        if targeting
        else None,
    )


async def serialize_ad(campaign: Campaigns) -> Ad:
    advertiser: Advertisers = await campaign.advertiser

    return Ad(
        ad_id=campaign.id,
        ad_title=campaign.ad_title,
        ad_text=campaign.ad_text,
        advertiser_id=advertiser.id,
    )


def calculate_ad_efficiency(ad: Campaigns, client_prob: float) -> float:
    if ad.impressions_count < AD_MIN_IMPRESSIONS:
        return 0
    ad_click_probability = ad.clicks_count / ad.impressions_count
    efficiency = (
        (
            ad.cost_per_impression * 3
            + ad.cost_per_click * (ad_click_probability + client_prob) / 2
        )
        * (
            1
            - (
                max(IMPRESSIONS_THRESHOLD, ad.impressions_count / ad.impressions_limit)
                - IMPRESSIONS_THRESHOLD
            )
            / (1.1 - IMPRESSIONS_THRESHOLD)
        )
        * (
            1
            - (
                max(CLICKS_THRESHOLD, ad.clicks_count / ad.clicks_limit)
                - CLICKS_THRESHOLD
            )
            / (1.1 - CLICKS_THRESHOLD)
        )
    )
    efficiency += min(
        math.log((ad.ml_score or ML_SCORE_DEFAULT) + 1) * ML_SCORE_LOG_MULT,
        efficiency * 0.25,
    )
    return efficiency


def calculate_stats(
    impressions_count: int,
    clicks_count: int,
    impressions_spent: float | int,
    clicks_spent: float | int,
    date: int | None = None,
) -> CampaignStats | CampaignDailyStats:
    conversion = (
        (clicks_count / impressions_count) * 100 if impressions_count > 0 else 0
    )
    spent_total = impressions_spent + clicks_spent

    stats = CampaignStats(
        impressions_count=impressions_count,
        clicks_count=clicks_count,
        conversion=conversion,
        spent_impressions=impressions_spent,
        spent_clicks=clicks_spent,
        spent_total=spent_total,
    )
    if date is not None:
        stats = stats.model_dump()
        stats['date'] = date
        stats = CampaignDailyStats.model_validate(stats)

    return stats
