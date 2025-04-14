from .time import get_current_date
from .. import s3_client, api_config
from ..utils import serialize_campaign
from adsplatform.db.models import Advertisers, CampaignsTargeting, Campaigns
from adsplatform.schemas.campaigns import CampaignEdit, CampaignIn, Campaign
from adsplatform.schemas.queries import PaginationQuery
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix='/advertisers/{advertiser_id}', tags=['Campaigns'])


@router.post('/campaigns', status_code=201)
async def create_campaign(advertiser_id: UUID, data: CampaignIn) -> Campaign:
    advertiser = await Advertisers.get_or_none(id=advertiser_id)
    if not advertiser:
        raise HTTPException(status_code=404, detail='Advertiser not found')

    current_date = (await get_current_date()).current_date

    if data.ad_image is not None and not await s3_client.key_exists(
        bucket=api_config.minio_bucket_name, key=data.ad_image
    ):
        raise HTTPException(status_code=404, detail='Provided image not found')

    if data.start_date < current_date:
        raise HTTPException(status_code=400, detail='Start date cannot be before current date')

    if data.end_date < current_date:
        raise HTTPException(status_code=400, detail='End date cannot be before current date')

    targeting = await CampaignsTargeting.create(
        **(data.targeting.model_dump(exclude_none=True) if data.targeting else {})
    )

    campaign = await Campaigns.create(
        **data.model_dump(exclude={'targeting'}),
        targeting=targeting,
        advertiser=advertiser,
    )

    return await serialize_campaign(campaign)


@router.get('/campaigns')
async def get_campaigns(
    advertiser_id: UUID, query: Annotated[PaginationQuery, Query()]
) -> list[Campaign]:
    advertiser = await Advertisers.get_or_none(id=advertiser_id)
    if not advertiser:
        raise HTTPException(status_code=404, detail='Advertiser not found')

    campaigns = advertiser.campaigns.all()
    if query.size is not None and query.page is not None:
        campaigns = campaigns.offset(query.page * query.size).limit(query.size)

    return [await serialize_campaign(campaign) for campaign in await campaigns]


@router.get('/campaigns/{campaign_id}')
async def get_campaign(advertiser_id: UUID, campaign_id: UUID) -> Campaign:
    advertiser = await Advertisers.get_or_none(id=advertiser_id)
    if not advertiser:
        raise HTTPException(status_code=404, detail='Advertiser not found')

    campaign = await Campaigns.get_or_none(id=campaign_id, advertiser=advertiser)
    if not campaign:
        raise HTTPException(status_code=404, detail='Campaign not found')

    return await serialize_campaign(campaign)


@router.put('/campaigns/{campaign_id}')
async def update_campaign(
    advertiser_id: UUID, campaign_id: UUID, data: CampaignEdit
) -> Campaign:
    advertiser = await Advertisers.get_or_none(id=advertiser_id)
    if not advertiser:
        raise HTTPException(status_code=404, detail='Advertiser not found')

    campaign = await Campaigns.get_or_none(
        id=campaign_id, advertiser=advertiser
    ).prefetch_related('targeting')
    if not campaign:
        raise HTTPException(status_code=404, detail='Campaign not found')

    current_date = (await get_current_date()).current_date

    if data.ad_image is not None and not await s3_client.key_exists(
        bucket=api_config.minio_bucket_name, key=data.ad_image
    ):
        raise HTTPException(status_code=404, detail='Provided image not found')

    if (
        current_date >= campaign.start_date
        and data.start_date is not None
        and data.start_date != campaign.start_date
    ):
        raise HTTPException(
            status_code=400, detail='Start date cannot be changed after campaign start'
        )

    if (
        current_date >= campaign.start_date
        and data.end_date is not None
        and data.end_date != campaign.end_date
    ):
        raise HTTPException(
            status_code=400, detail='End date cannot be changed after campaign start'
        )

    if (
        current_date >= campaign.start_date
        and data.impressions_limit is not None
        and data.impressions_limit != campaign.impressions_limit
    ):
        raise HTTPException(
            status_code=400,
            detail='Impressions limit cannot be changed after campaign start',
        )

    if (
        current_date >= campaign.start_date
        and data.clicks_limit is not None
        and data.clicks_limit != campaign.clicks_limit
    ):
        raise HTTPException(
            status_code=400,
            detail='Clicks limit cannot be changed after campaign start',
        )

    if data.start_date is not None and data.start_date != campaign.start_date and data.start_date < current_date:
        raise HTTPException(status_code=400, detail='Start date cannot be before current date')

    if data.end_date is not None and data.end_date != campaign.end_date and data.end_date < current_date:
        raise HTTPException(status_code=400, detail='End date cannot be before current date')

    if (
        data.impressions_limit is not None
        and data.impressions_limit < await campaign.impressions.all().count()
    ):
        raise HTTPException(
            status_code=400,
            detail='Impressions limit cannot be less than impressions count',
        )

    if (
        data.clicks_limit is not None
        and data.clicks_limit < await campaign.clicks.all().count()
    ):
        raise HTTPException(
            status_code=400, detail='Clicks limit cannot be less than clicks count'
        )

    if data.start_date is not None and (
        campaign.end_date is not None
        and data.start_date > campaign.end_date
        or (data.end_date is not None and data.start_date > data.end_date)
    ):
        raise HTTPException(
            status_code=400,
            detail='Start date can not be greater than end date',
        )

    if data.end_date is not None and (
        campaign.start_date is not None
        and data.end_date < campaign.start_date
        or (data.start_date is not None and data.end_date < data.start_date)
    ):
        raise HTTPException(
            status_code=400, detail='End date can not be lower than start date'
        )

    if data.targeting is not None:
        await campaign.targeting.update_from_dict(data.targeting.model_dump())
        await campaign.targeting.save()

    try:
        await campaign.update_from_dict(data.model_dump(exclude={'targeting'}))
        await campaign.save()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Unable to update campaign: {e}")

    return await serialize_campaign(campaign)


@router.delete('/campaigns/{campaign_id}', status_code=204)
async def delete_campaign(advertiser_id: UUID, campaign_id: UUID):
    advertiser = await Advertisers.get_or_none(id=advertiser_id)
    if not advertiser:
        raise HTTPException(status_code=404, detail='Advertiser not found')

    campaign = await Campaigns.get_or_none(id=campaign_id, advertiser=advertiser)
    if not campaign:
        raise HTTPException(status_code=404, detail='Campaign not found')

    await campaign.delete()
