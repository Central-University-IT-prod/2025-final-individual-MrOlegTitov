import uuid
from adsplatform.bot.utils import serialize_campaign
from adsplatform.schemas.campaigns import Campaign, CampaignTargeting

import pytest


def test_serialize_campaign():
    campaign = Campaign(
        impressions_limit=50,
        clicks_limit=25,
        cost_per_impression=0.5,
        cost_per_click=1,
        start_date=0,
        end_date=1,
        ad_title='Test ad',
        ad_text='Test ad',
        campaign_id=uuid.uuid4(),
        advertiser_id=uuid.uuid4(),
    )
    text = serialize_campaign(campaign)

    assert len(text) > 0


def test_serialize_invalid_limits_campaign():
    campaign = None
    text = None
    with pytest.raises(ValueError):
        campaign = Campaign(
            impressions_limit=25,
            clicks_limit=50,
            cost_per_impression=0.5,
            cost_per_click=1,
            start_date=0,
            end_date=1,
            ad_title='Test ad',
            ad_text='Test ad',
            campaign_id=uuid.uuid4(),
            advertiser_id=uuid.uuid4(),
        )
        text = serialize_campaign(campaign)

    assert campaign is None and text is None


def test_serialize_invalid_dates_campaign():
    campaign = None
    text = None
    with pytest.raises(ValueError):
        campaign = Campaign(
            impressions_limit=50,
            clicks_limit=25,
            cost_per_impression=0.5,
            cost_per_click=1,
            start_date=20,
            end_date=10,
            ad_title='Test ad',
            ad_text='Test ad',
            campaign_id=uuid.uuid4(),
            advertiser_id=uuid.uuid4(),
        )
        text = serialize_campaign(campaign)

    assert campaign is None and text is None


def test_serialize_invalid_costs_campaign():
    campaign = None
    text = None
    with pytest.raises(ValueError):
        campaign = Campaign(
            impressions_limit=50,
            clicks_limit=25,
            cost_per_impression=0,
            cost_per_click=0,
            start_date=0,
            end_date=1,
            ad_title='Test ad',
            ad_text='Test ad',
            campaign_id=uuid.uuid4(),
            advertiser_id=uuid.uuid4(),
        )
        text = serialize_campaign(campaign)

    assert campaign is None and text is None


def test_serialize_invalid_targeting_campaign():
    campaign = None
    text = None
    with pytest.raises(ValueError):
        campaign = Campaign(
            impressions_limit=50,
            clicks_limit=25,
            cost_per_impression=0.5,
            cost_per_click=1,
            start_date=0,
            end_date=1,
            ad_title='Test ad',
            ad_text='Test ad',
            campaign_id=uuid.uuid4(),
            advertiser_id=uuid.uuid4(),
            targeting=CampaignTargeting(age_from=100, age_to=10),
        )
        text = serialize_campaign(campaign)

    assert campaign is None and text is None
