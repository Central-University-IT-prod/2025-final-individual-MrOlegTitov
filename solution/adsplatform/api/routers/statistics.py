from adsplatform.api.utils import calculate_stats
from adsplatform.db.models import (
    Campaigns,
    Advertisers,
    CampaignClicks,
    CampaignImpressions,
)
from adsplatform.schemas.statistics import CampaignStats, CampaignDailyStats
from itertools import chain
from uuid import UUID

from fastapi import APIRouter, HTTPException

from tortoise.expressions import Subquery, RawSQL
from tortoise.functions import Min, Max

router = APIRouter(prefix='/stats', tags=['Statistics'])


@router.get('/campaigns/{campaign_id}')
async def campaign_stats(campaign_id: UUID) -> CampaignStats:
    campaign = await Campaigns.get_or_none(id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail='Campaign not found')

    impression_prices = sum(
        await campaign.impressions.all().values_list('price', flat=True)
    )
    clicks_prices = sum(await campaign.clicks.all().values_list('price', flat=True))

    return calculate_stats(
        impressions_count=await campaign.impressions.all().count(),
        clicks_count=await campaign.clicks.all().count(),
        impressions_spent=impression_prices,
        clicks_spent=clicks_prices,
    )


@router.get('/advertisers/{advertiser_id}/campaigns')
async def advertiser_stats(advertiser_id: UUID) -> CampaignStats:
    impressions_subquery = CampaignImpressions.filter(
        campaign=RawSQL('"campaigns"."id"')
    ).count()
    clicks_subquery = CampaignClicks.filter(campaign=RawSQL('"campaigns"."id"')).count()

    advertiser = await Advertisers.get_or_none(id=advertiser_id)
    if not advertiser:
        raise HTTPException(status_code=404, detail='Advertiser not found')

    campaigns = await Campaigns.filter(advertiser=advertiser).annotate(
        impressions_count=Subquery(impressions_subquery),
        clicks_count=Subquery(clicks_subquery),
    )
    impressions_count = sum([campaign.impressions_count for campaign in campaigns])
    clicks_count = sum([campaign.clicks_count for campaign in campaigns])
    impression_prices = sum(
        await CampaignImpressions.filter(campaign__advertiser=advertiser).values_list(
            'price', flat=True
        )
    )
    clicks_prices = sum(
        await CampaignClicks.filter(campaign__advertiser=advertiser).values_list(
            'price', flat=True
        )
    )

    return calculate_stats(
        impressions_count=impressions_count,
        clicks_count=clicks_count,
        impressions_spent=impression_prices,
        clicks_spent=clicks_prices,
    )


@router.get('/campaigns/{campaign_id}/daily')
async def campaign_daily_stats(campaign_id: UUID) -> list[CampaignDailyStats]:
    campaign = await Campaigns.get_or_none(id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail='Campaign not found')

    impressions_date = await campaign.impressions.all().values_list('date', flat=True)
    clicks_date = await campaign.clicks.all().values_list('date', flat=True)

    if not impressions_date:
        impressions_date = [0]
    if not clicks_date:
        clicks_date = [0]

    min_date = min(*impressions_date, *clicks_date)
    max_date = max(*impressions_date, *clicks_date)

    daily_stats = []
    for date in range(min_date, max_date + 1):
        impressions_count = await campaign.impressions.filter(date=date).count()
        clicks_count = await campaign.clicks.filter(date=date).count()
        impression_prices = sum(
            await campaign.impressions.filter(date=date).values_list('price', flat=True)
        )
        click_prices = sum(
            await campaign.clicks.filter(date=date).values_list('price', flat=True)
        )
        daily_stats.append(
            calculate_stats(
                impressions_count=impressions_count,
                clicks_count=clicks_count,
                impressions_spent=impression_prices,
                clicks_spent=click_prices,
                date=date,
            )
        )

    return daily_stats


@router.get('/advertisers/{advertiser_id}/campaigns/daily')
async def advertiser_daily_stats(advertiser_id: UUID) -> list[CampaignDailyStats]:
    advertiser = await Advertisers.get_or_none(id=advertiser_id)
    if not advertiser:
        raise HTTPException(status_code=404, detail='Advertiser not found')

    campaigns = await Campaigns.filter(advertiser=advertiser).annotate(
        impressions_min_date=Min('impressions__date'),
        impressions_max_date=Max('impressions__date'),
        clicks_min_date=Min('clicks__date'),
        clicks_max_date=Max('clicks__date'),
    )

    if not campaigns:
        return []

    min_date = min(
        chain.from_iterable(
            (campaign.impressions_min_date or 0, campaign.clicks_min_date or 0)
            for campaign in campaigns
        )
    )
    max_date = max(
        chain.from_iterable(
            (campaign.impressions_max_date or 0, campaign.clicks_max_date or 0)
            for campaign in campaigns
        )
    )

    daily_stats = []
    for date in range(min_date, max_date + 1):
        impressions_count = sum(
            [
                await campaign.impressions.filter(date=date).count()
                for campaign in campaigns
            ]
        )
        clicks_count = sum(
            [await campaign.clicks.filter(date=date).count() for campaign in campaigns]
        )
        impression_prices = sum(
            chain.from_iterable(
                [
                    await campaign.impressions.filter(date=date).values_list(
                        'price', flat=True
                    )
                    for campaign in campaigns
                ]
            )
        )
        click_prices = sum(
            chain.from_iterable(
                [
                    await campaign.clicks.filter(date=date).values_list(
                        'price', flat=True
                    )
                    for campaign in campaigns
                ]
            )
        )

        daily_stats.append(
            calculate_stats(
                impressions_count=impressions_count,
                clicks_count=clicks_count,
                impressions_spent=impression_prices,
                clicks_spent=click_prices,
                date=date,
            )
        )

    return daily_stats
