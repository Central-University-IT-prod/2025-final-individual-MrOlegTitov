import random
from .time import get_current_date
from adsplatform.api.utils import (
    AD_RANDOM_CHANCE,
    USER_MIN_IMPRESSIONS,
    serialize_ad,
    calculate_ad_efficiency,
)
from adsplatform.db.models import (
    Campaigns,
    Clients,
    MLScores,
    CampaignImpressions,
    CampaignClicks,
)
from adsplatform.schemas.ads import Ad
from adsplatform.schemas.campaigns import TargetingGender
from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException

from tortoise.expressions import Q, Subquery, RawSQL
from tortoise.functions import Count

router = APIRouter(prefix='/ads', tags=['Ads'])


@router.get('')
async def get_ad(client_id: UUID) -> Ad:
    client = await Clients.get_or_none(id=client_id).annotate(
        impressions_count=Count('impressions'), clicks_count=Count('clicks')
    )
    if not client:
        raise HTTPException(status_code=404, detail='Client not found')

    current_date = (await get_current_date()).current_date

    campaigns = Campaigns.filter(
        Q(
            start_date__lte=current_date,
            start_date__isnull=True,
            join_type='OR',
        ),
        Q(
            end_date__gte=current_date,
            end_date__isnull=True,
            join_type='OR',
        ),  # Active ads
        Q(
            targeting__age_from__lte=client.age,
            targeting__age_from__isnull=True,
            join_type='OR',
        ),
        Q(
            targeting__age_to__gte=client.age,
            targeting__age_to__isnull=True,
            join_type='OR',
        ),
        Q(
            targeting__location__iexact=client.location,
            targeting__location__isnull=True,
            join_type='OR',
        ),
        Q(
            targeting__gender__in=[client.gender, TargetingGender.ALL],
            targeting__gender__isnull=True,
            join_type='OR',
        ),  # Targeting
    )

    ml_score_subquery = MLScores.filter(
        client=client, advertiser=RawSQL('"campaigns"."advertiser_id"')
    ).values("score")

    campaigns = campaigns.annotate(
        ml_score=Subquery(ml_score_subquery),
        impressions_count=Count('impressions'),
        clicks_count=Count('clicks'),
    )
    campaigns = await campaigns  # Executing the complex SQL query we created earlier

    client_click_probability = (
        (client.clicks_count / client.impressions_count)
        if client.impressions_count >= USER_MIN_IMPRESSIONS
        else 0
    )
    campaigns = {
        ad: calculate_ad_efficiency(ad=ad, client_prob=client_click_probability)
        for ad in campaigns
    }
    non_relevant_campaigns = list(
        filter(lambda ad: campaigns[ad] == 0, campaigns.keys())
    )

    if not campaigns and not non_relevant_campaigns:
        raise HTTPException(status_code=404, detail='Ad not found')

    if random.randint(0, 100) > AD_RANDOM_CHANCE or not non_relevant_campaigns:
        campaign = list(
            sorted(list(campaigns.keys()), key=lambda ad: campaigns[ad], reverse=True)
        )[0]
    else:
        campaign = random.choice(non_relevant_campaigns)

    if not await CampaignImpressions.exists(campaign=campaign, client=client):
        await CampaignImpressions.create(
            campaign=campaign,
            client=client,
            price=campaign.cost_per_impression,
            date=current_date,
        )

    return await serialize_ad(campaign)


@router.post('/{ad_id}/click', status_code=204)
async def click_ad(ad_id: UUID, client_id: Annotated[UUID, Body(embed=True)]) -> None:
    client = await Clients.get_or_none(id=client_id)
    if not client:
        raise HTTPException(status_code=404, detail='Client not found')

    campaign = await Campaigns.get_or_none(id=ad_id)
    if not campaign:
        raise HTTPException(status_code=404, detail='Campaign not found')

    if not await campaign.impressions.filter(client=client).exists():
        raise HTTPException(status_code=403, detail='You cannot click unseen campaign')

    if not await CampaignClicks.exists(campaign=campaign, client=client):
        await CampaignClicks.create(
            campaign=campaign,
            client=client,
            price=campaign.cost_per_click,
            date=(await get_current_date()).current_date,
        )
