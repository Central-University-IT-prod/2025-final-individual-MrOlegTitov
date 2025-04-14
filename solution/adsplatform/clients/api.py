from ..schemas.campaigns import Campaign
from ..schemas.statistics import CampaignStats, CampaignDailyStats
from typing import Any
from urllib.parse import quote_plus

import httpx


class APIClient(httpx.AsyncClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def get_s3_file(self, key: str) -> bytes:
        resp = await self.get(f"/s3/{quote_plus(key, safe='/')}")
        if resp.status_code == 404:
            resp_data = resp.json()
            raise Exception(resp_data.get('message'))

        return resp.content

    async def upload_s3_file(self, key: str, data: bytes, content_type: str) -> None:
        resp = await self.put(
            f"/s3/{quote_plus(key, safe='/')}",
            files={'file': (key.split('/')[-1], data, content_type)},
        )
        if resp.status_code != 201:
            resp_data = resp.json()
            raise Exception(resp_data.get('message'))

    async def delete_s3_file(self, key: str) -> None:
        resp = await self.delete(f"/s3/{quote_plus(key, safe='/')}")
        if resp.status_code != 204:
            resp_data = resp.json()
            raise Exception(resp_data.get('message'))

    async def create_campaign(
        self, advertiser_id: str, data: dict[str, Any]
    ) -> Campaign:
        resp = await self.post(f"/advertisers/{advertiser_id}/campaigns", json=data)
        if resp.status_code != 201:
            resp_data = resp.json()
            raise Exception(resp_data.get('message'))

        return Campaign.model_validate(resp.json())

    async def list_campaigns(
        self, advertiser_id: str, page: int | None = None, size: int | None = None
    ) -> list[Campaign]:
        resp = await self.get(
            f"/advertisers/{advertiser_id}/campaigns",
            params={'page': page, 'size': size}
            if size is not None and page is not None
            else {},
        )
        if resp.status_code != 200:
            resp_data = resp.json()
            raise Exception(resp_data.get('message'))

        return list(map(lambda c: Campaign.model_validate(c), resp.json()))

    async def get_campaign(self, advertiser_id: str, campaign_id: str) -> Campaign:
        resp = await self.get(f"/advertisers/{advertiser_id}/campaigns/{campaign_id}")
        if resp.status_code != 200:
            resp_data = resp.json()
            raise Exception(resp_data.get('message'))

        return Campaign.model_validate(resp.json())

    async def update_campaign(
        self, advertiser_id: str, campaign_id: str, data: dict
    ) -> Campaign:
        resp = await self.put(
            f"/advertisers/{advertiser_id}/campaigns/{campaign_id}", json=data
        )
        if resp.status_code != 200:
            resp_data = resp.json()
            raise Exception(resp_data.get('message'))

        return Campaign.model_validate(resp.json())

    async def delete_campaign(self, advertiser_id: str, campaign_id: str) -> None:
        resp = await self.delete(
            f"/advertisers/{advertiser_id}/campaigns/{campaign_id}"
        )
        if resp.status_code != 204:
            resp_data = resp.json()
            raise Exception(resp_data.get('message'))

    async def get_campaign_stats(self, campaign_id: str) -> CampaignStats:
        resp = await self.get(f"/stats/campaigns/{campaign_id}")
        if resp.status_code != 200:
            resp_data = resp.json()
            raise Exception(resp_data.get('message'))

        return CampaignStats.model_validate(resp.json())

    async def get_advertiser_stats(self, advertiser_id: str) -> CampaignStats:
        resp = await self.get(f"/stats/advertisers/{advertiser_id}/campaigns")
        if resp.status_code != 200:
            resp_data = resp.json()
            raise Exception(resp_data.get('message'))

        return CampaignStats.model_validate(resp.json())

    async def get_campaign_daily_stats(
        self, campaign_id: str
    ) -> list[CampaignDailyStats]:
        resp = await self.get(f"/stats/campaigns/{campaign_id}/daily")
        if resp.status_code != 200:
            resp_data = resp.json()
            raise Exception(resp_data.get('message'))

        return list(map(lambda s: CampaignDailyStats.model_validate(s), resp.json()))

    async def get_advertiser_daily_stats(
        self, advertiser_id: str
    ) -> list[CampaignDailyStats]:
        resp = await self.get(f"/stats/advertisers/{advertiser_id}/campaigns/daily")
        if resp.status_code != 200:
            resp_data = resp.json()
            raise Exception(resp_data.get('message'))

        return list(map(lambda s: CampaignDailyStats.model_validate(s), resp.json()))
