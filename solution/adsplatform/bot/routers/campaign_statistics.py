from .. import api_client
from .campaign_list import send_statistics, send_list
from ..keyboards.fabric import (
    CampaignStatistics,
    StatisticsActions,
    daily_statistics_kb,
)
from ..middlewares.user import UserMiddleware
from ..utils import serialize_daily_statistics
from adsplatform.db.models import TelegramUsers
from contextlib import suppress
from typing import Callable, Awaitable
from uuid import UUID

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.exceptions import TelegramBadRequest

router = Router()
router.callback_query.middleware(UserMiddleware())


async def send_daily_statistics(
    message: Message,
    page: int,
    campaign_id: UUID | str,
    week: int,
) -> None:
    try:
        daily_stats = await api_client.get_campaign_daily_stats(
            campaign_id=str(campaign_id)
        )
    except:
        await message.edit_text(text='Рекламная кампания не найдена')
        await message.delete_reply_markup()
        return

    weeks_count = len(daily_stats) // 7
    if week == -1:
        week = max(weeks_count - 1, 0)
    if week > weeks_count:
        week = 0

    daily_stats = daily_stats[week * 7 : week * 7 + 7]
    text = serialize_daily_statistics(
        stats=daily_stats,
        start_date=week * 7,
        end_date=week * 7 + 7,
        is_advertiser=False,
    )

    with suppress(TelegramBadRequest):
        await message.edit_text(
            text=text,
            reply_markup=daily_statistics_kb(
                campaign_id=campaign_id,
                page=page,
                week=week,
            ),
        )


TYPES_ACTIONS: dict[
    StatisticsActions,
    Callable[[Message, int, UUID, int | None], Awaitable[None]],
] = {
    StatisticsActions.DAILY: send_daily_statistics,
    StatisticsActions.TOTAL: send_statistics,
}


@router.callback_query(CampaignStatistics.filter(F.action.in_(TYPES_ACTIONS.keys())))
async def change_statistics_type(
    call: CallbackQuery, callback_data: CampaignStatistics
) -> None:
    type_func = TYPES_ACTIONS[callback_data.action]
    await type_func(
        call.message,
        callback_data.page,
        callback_data.campaign_id,
        callback_data.week or -1,
    )
    await call.answer()


@router.callback_query(CampaignStatistics.filter(F.action == StatisticsActions.NEXT))
async def next_week(call: CallbackQuery, callback_data: CampaignStatistics) -> None:
    week = (callback_data.week or -1) + 1
    await send_daily_statistics(
        message=call.message,
        page=callback_data.page,
        campaign_id=callback_data.campaign_id,
        week=week,
    )
    await call.answer()


@router.callback_query(
    CampaignStatistics.filter(F.action == StatisticsActions.PREVIOUS)
)
async def previous_week(call: CallbackQuery, callback_data: CampaignStatistics) -> None:
    week = max((callback_data.week or -1) - 1, -1)
    await send_daily_statistics(
        message=call.message,
        page=callback_data.page,
        campaign_id=callback_data.campaign_id,
        week=week,
    )
    await call.answer()


@router.callback_query(CampaignStatistics.filter(F.action == StatisticsActions.BACK))
async def back_to_list(
    call: CallbackQuery, callback_data: CampaignStatistics, user: TelegramUsers
) -> None:
    await send_list(
        message=call.message,
        user=user,
        campaign_id=callback_data.campaign_id,
        page=callback_data.page,
        edit_text=True,
    )
    await call.answer()
