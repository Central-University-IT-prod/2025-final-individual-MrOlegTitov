from .. import api_client
from ..keyboards.fabric import (
    StatisticsActions,
    daily_statistics_kb,
    total_statistics_kb,
    AdvertiserStatistics,
)
from ..middlewares.user import UserMiddleware
from ..utils import serialize_daily_statistics, serialize_statistics
from adsplatform.db.models import TelegramUsers
from contextlib import suppress
from typing import Awaitable, Callable

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

router = Router()
router.message.middleware(UserMiddleware())
router.callback_query.middleware(UserMiddleware())


async def send_statistics(
    message: Message,
    user: TelegramUsers,
    week: int | None = None,
    edit_text: bool = True,
) -> None:
    stats = await api_client.get_advertiser_stats(advertiser_id=str(user.advertiser.id))
    text = serialize_statistics(stats=stats, is_advertiser=True)

    if edit_text:
        with suppress(TelegramBadRequest):
            await message.edit_text(
                text=text,
                reply_markup=total_statistics_kb(
                    week=week,
                ),
            )
    else:
        await message.answer(
            text=text,
            reply_markup=total_statistics_kb(
                week=week,
            ),
        )


async def send_daily_statistics(
    message: Message, user: TelegramUsers, week: int, edit_text: bool = True
) -> None:
    daily_stats = await api_client.get_advertiser_daily_stats(
        advertiser_id=str(user.advertiser.id)
    )

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

    if edit_text:
        with suppress(TelegramBadRequest):
            await message.edit_text(
                text=text,
                reply_markup=daily_statistics_kb(
                    week=week,
                ),
            )
    else:
        await message.answer(
            text=text,
            reply_markup=daily_statistics_kb(
                week=week,
            ),
        )


TYPES_ACTIONS: dict[
    StatisticsActions,
    Callable[[Message, TelegramUsers, int | None, bool], Awaitable[None]],
] = {
    StatisticsActions.DAILY: send_daily_statistics,
    StatisticsActions.TOTAL: send_statistics,
}


@router.message(F.text == '📊 Моя статистика', StateFilter(None))
async def my_statistics(message: Message, user: TelegramUsers) -> None:
    await send_statistics(message=message, user=user, edit_text=False)


@router.callback_query(AdvertiserStatistics.filter(F.action.in_(TYPES_ACTIONS.keys())))
async def change_statistics_type(
    call: CallbackQuery, callback_data: AdvertiserStatistics, user: TelegramUsers
) -> None:
    type_func = TYPES_ACTIONS[callback_data.action]
    await type_func(call.message, user, callback_data.week or -1, True)
    await call.answer()


@router.callback_query(AdvertiserStatistics.filter(F.action == StatisticsActions.NEXT))
async def next_week(
    call: CallbackQuery, callback_data: AdvertiserStatistics, user: TelegramUsers
) -> None:
    week = (callback_data.week or -1) + 1
    await send_daily_statistics(
        message=call.message,
        user=user,
        week=week,
        edit_text=True,
    )
    await call.answer()


@router.callback_query(
    AdvertiserStatistics.filter(F.action == StatisticsActions.PREVIOUS)
)
async def previous_week(
    call: CallbackQuery, callback_data: AdvertiserStatistics, user: TelegramUsers
) -> None:
    week = max((callback_data.week or -1) - 1, -1)
    await send_daily_statistics(
        message=call.message,
        user=user,
        week=week,
        edit_text=True,
    )
    await call.answer()
