from adsplatform.config import APIConfig
from adsplatform.clients.yandexgpt import YandexGPTClientAsync

import pytest

pytestmark = pytest.mark.asyncio

config = APIConfig()

client = YandexGPTClientAsync(
    folder_id=config.yandex_folder_id, api_key=config.yandex_api_key
)


async def test_ad_text_generation():
    text = await client.generate_ad_text(
        ad_title='Повышенный кешбэк 15% для новых клиентов банка!',
        advertiser_name='Т-Банк',
    )
    assert len(text) > 0
