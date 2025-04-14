from .. import redis_client
from adsplatform.schemas.time import Time

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix='/time', tags=['Time'])


@router.post('/advance')
async def set_current_date(data: Time) -> Time:
    current_date = await get_current_date()
    if data.current_date < current_date.current_date:
        raise HTTPException(
            status_code=400, detail='New date cannot be lower than current date'
        )

    await redis_client.set('current_date', data.current_date)

    return Time(current_date=data.current_date)


@router.get('')
async def get_current_date() -> Time:
    current_date = await redis_client.get('current_date')
    if current_date is None:
        current_date = 0
        await redis_client.set('current_date', current_date)

    return Time(current_date=int(current_date))
