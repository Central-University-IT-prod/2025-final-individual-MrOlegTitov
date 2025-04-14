import asyncio
import json

import httpx

MODERATION_TASK = (
    'Определи, содержит ли текст ненормативную лексику или иной небезопасный контент. '
    'Если текст небезопасный, то постарайся определить категорию, '
    'к которой его можно отнести'
)
MODERATION_LABELS = [
    'допустимое',
    'оскорбления',
    'ненормативная лексика',
    'призывы к насилию',
    'контент для взрослых',
    'призыв к терроризму',
    'призыв к совершению незаконных действий',
    'иной небезопасный контент',
]

TEXT_GENERATION_TASK = (
    'Сгенерируй короткий текст (около 125 символов), который будет использован в '
    'рекламной кампании на основе её заголовка и имени рекламодателя. '
    'Текст должен соответствовать теме рекламы и нормам русского языка'
)


class YandexAPIKeyAuth(httpx.Auth):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def auth_flow(self, request):
        request.headers['Authorization'] = f"Api-Key {self.api_key}"
        yield request


class YandexGPTClientAsync(httpx.AsyncClient):
    def __init__(self, folder_id: str, api_key: str, model: str = 'yandexgpt-lite'):
        super().__init__(
            base_url='https://llm.api.cloud.yandex.net/foundationModels/v1',
            auth=YandexAPIKeyAuth(api_key=api_key),
            timeout=10,
        )

        self._moderation_model = f"cls://{folder_id}/{model}/latest"
        self._generation_model = f"gpt://{folder_id}/{model}/latest"

    async def moderate_text(self, text: str) -> tuple[bool, str | None]:
        """
        Checks whether the specified text passes content safety moderation

        :param text: Text to be moderated
        :return: Whether the text is safe and the category of unsafe content otherwise
        """
        data = {
            "modelUri": self._moderation_model,
            "text": text,
            "task_description": MODERATION_TASK,
            "labels": MODERATION_LABELS,
        }

        resp = None
        for _ in range(5):  # Retry if response code was 429
            resp = await self.post(url='/fewShotTextClassification', json=data)
            if resp.status_code == 200:
                break
            await asyncio.sleep(2)
        if not resp:
            return False, None

        resp.raise_for_status()

        res: list[dict[str, str | float]] = resp.json().get('predictions')
        res_label = sorted(
            res, key=lambda label: label.get('confidence', 0), reverse=True
        )[0]
        if res_label.get('label') == MODERATION_LABELS[0]:
            return True, None

        return False, res_label.get('label')

    async def generate_ad_text(self, ad_title: str, advertiser_name: str) -> str:
        """
        Generates text that can be used in an advertisement based on its title and the advertiser's name

        :param ad_title: Ad title
        :param advertiser_name: Name of advertiser
        :return: Generated text
        """
        data = {
            "modelUri": self._generation_model,
            "completionOptions": {
                "stream": False,
                "temperature": 0.5,
                "reasoningOptions": {"mode": "DISABLED"},
            },
            "messages": [
                {'role': 'system', 'text': TEXT_GENERATION_TASK},
                {
                    'role': 'user',
                    'text': json.dumps(
                        {
                            'заголовок рекламы': ad_title,
                            'имя рекламодателя': advertiser_name,
                        }
                    ),
                },
            ],
        }
        resp = None
        for _ in range(5):  # Retry if response code was 429
            resp = await self.post(url='/completion', json=data)
            if resp.status_code == 200:
                break
            await asyncio.sleep(2)
        if not resp:
            return ''

        resp.raise_for_status()

        res: list[dict[str, dict[str, str] | str]] = (
            resp.json().get('result', {}).get('alternatives', [])
        )
        if not res:
            return ''

        return res[0].get('message', {}).get('text', '')
