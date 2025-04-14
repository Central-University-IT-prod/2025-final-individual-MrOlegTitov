from adsplatform.bot.utils import serialize_statistics, serialize_daily_statistics
from adsplatform.schemas.statistics import CampaignStats, CampaignDailyStats


def test_campaign_stats_serialization():
    stats = CampaignStats(
        impressions_count=20,
        clicks_count=10,
        conversion=0.5,
        spent_impressions=52,
        spent_clicks=104,
        spent_total=156,
    )
    text = serialize_statistics(stats, is_advertiser=False)

    assert len(text) > 0


def test_campaign_daily_stats_serialization():
    stats = CampaignDailyStats(
        impressions_count=20,
        clicks_count=10,
        conversion=0.5,
        spent_impressions=52,
        spent_clicks=104,
        spent_total=156,
        date=0,
    )
    text = serialize_daily_statistics(
        stats=[stats], start_date=0, end_date=0, is_advertiser=False
    )

    assert len(text) > 0
