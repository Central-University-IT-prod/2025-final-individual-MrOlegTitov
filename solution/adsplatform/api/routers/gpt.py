from .. import yandex_client
from adsplatform.schemas.gpt import AdTextGenerationIn, TextModerationOut
from typing import Annotated

from fastapi import APIRouter, Body

router = APIRouter(prefix='/gpt', tags=['GPT'])


@router.post('/moderate_text')
async def moderate_text(text: Annotated[str, Body(embed=True)]) -> TextModerationOut:
    is_safe, category = await yandex_client.moderate_text(text)

    return TextModerationOut(
        is_safe=is_safe,
        unsafe_category=category,
    )


@router.post('/generate_text')
async def generate_text(data: AdTextGenerationIn) -> str:
    return await yandex_client.generate_ad_text(**data.model_dump())
