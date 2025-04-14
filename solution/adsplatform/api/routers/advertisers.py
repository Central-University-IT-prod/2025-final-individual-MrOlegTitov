from ..utils import serialize_advertiser
from adsplatform.db.models import Advertisers, MLScores, Clients
from adsplatform.schemas.advertisers import Advertiser, MLScore
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, HTTPException

router = APIRouter(prefix='/advertisers', tags=['Advertisers'])


@router.get('/{advertiser_id}')
async def get_advertiser(advertiser_id: UUID) -> Advertiser:
    advertiser = await Advertisers.get_or_none(id=advertiser_id)
    if not advertiser:
        raise HTTPException(status_code=404, detail='Advertiser not found')

    return serialize_advertiser(advertiser)


@router.post('/bulk', status_code=201)
async def bulk_update(data: Annotated[list[Advertiser], Body()]) -> list[Advertiser]:
    result = []
    for advertiser_data in data:
        advertiser = await Advertisers.get_or_none(id=advertiser_data.advertiser_id)
        if not advertiser:
            advertiser = await Advertisers.create(
                id=advertiser_data.advertiser_id,
                **advertiser_data.model_dump(
                    exclude_none=True, exclude={'advertiser_id'}
                ),
            )
        else:
            await advertiser.update_from_dict(
                advertiser_data.model_dump(exclude_none=True, exclude={'advertiser_id'})
            )
            await advertiser.save()

        result.append(serialize_advertiser(advertiser))

    return result


@router.post('/ml-scores')
async def set_score(data: MLScore) -> None:
    client = await Clients.get_or_none(id=data.client_id)
    if not client:
        raise HTTPException(status_code=404, detail='Client not found')
    advertiser = await Advertisers.get_or_none(id=data.advertiser_id)
    if not advertiser:
        raise HTTPException(status_code=404, detail='Advertiser not found')

    score = (
        await MLScores.get_or_create(
            client=client, advertiser=advertiser, defaults={'score': 0}
        )
    )[0]
    score.score = data.score
    await score.save()
