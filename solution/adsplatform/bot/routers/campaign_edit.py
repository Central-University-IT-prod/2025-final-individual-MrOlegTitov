from .campaign_list import send_list, send_edit_categories
from .. import api_client
from ..keyboards.fabric import (
    CampaignEdit,
    CampaignEditActions,
    campaign_edit_targeting_kb,
    campaign_edit_values_kb,
    campaign_edit_dates_kb,
    campaign_edit_info_kb,
)
from ..keyboards.reply import cancel_kb, targeting_gender_edit_kb
from ..middlewares.user import UserMiddleware
from ..states import CampaignState
from adsplatform.db.models import TelegramUsers
from contextlib import suppress
from typing import Callable
from uuid import UUID

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.state import State
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, ReplyKeyboardMarkup

router = Router()
router.callback_query.middleware(UserMiddleware())

MENU_ACTIONS: dict[
    CampaignEditActions, tuple[str, Callable[[UUID, int], InlineKeyboardMarkup]]
] = {
    CampaignEditActions.INFO: (
        '📄 <b>Основная информация</b>\n'
        '📢 <i>Вы можете изменить название, описание или изображение кампании.</i>\n'
        '✏️ Выберите, что хотите изменить:',
        campaign_edit_info_kb,
    ),
    CampaignEditActions.DATES: (
        '📆 <b>Даты кампании</b>\n'
        '⏳ <i>Здесь можно изменить дату начала и окончания рекламной кампании.</i>\n'
        '📅 Укажите нужные даты:',
        campaign_edit_dates_kb,
    ),
    CampaignEditActions.VALUES: (
        '🎯 <b>Целевые значения</b>\n'
        '💰 <i>Настройте целевые показатели и стоимость рекламной кампании.</i>\n'
        'Выберите параметр для изменения:',
        campaign_edit_values_kb,
    ),
    CampaignEditActions.TARGETING: (
        '🌍 <b>Таргетинг</b>\n'
        '🎯 <i>Задайте аудиторию, на которую будет направлена реклама.</i>\n'
        'Выберите, что хотите изменить:',
        campaign_edit_targeting_kb,
    ),
}

EDIT_ACTIONS: dict[
    CampaignEditActions, tuple[State, str, ReplyKeyboardMarkup | None]
] = {
    CampaignEditActions.AD_TITLE: (CampaignState.ad_title, 'новое название'),
    CampaignEditActions.AD_TEXT: (CampaignState.ad_text, 'новый текст'),
    CampaignEditActions.AD_IMAGE: (CampaignState.ad_image, 'новое изображение'),
    CampaignEditActions.START_DATE: (CampaignState.start_date, 'новую дату начала'),
    CampaignEditActions.END_DATE: (CampaignState.end_date, 'новую дату окончания'),
    CampaignEditActions.IMPRESSIONS_LIMIT: (
        CampaignState.impressions_limit,
        'новое целевое число просмотров',
    ),
    CampaignEditActions.CLICKS_LIMIT: (
        CampaignState.clicks_limit,
        'новое целевое число переходов',
    ),
    CampaignEditActions.COST_PER_IMPRESSION: (
        CampaignState.cost_per_impression,
        'новую стоимость одного просмотра',
    ),
    CampaignEditActions.COST_PER_CLICK: (
        CampaignState.cost_per_click,
        'новую стоимость одного перехода',
    ),
    CampaignEditActions.TARGETING_GENDER: (
        CampaignState.targeting_gender,
        'новый пол, для которого предназначена',
        targeting_gender_edit_kb,
    ),
    CampaignEditActions.TARGETING_AGE_FROM: (
        CampaignState.targeting_age_from,
        'новый минимальный возраст, для которого предназначена',
    ),
    CampaignEditActions.TARGETING_AGE_TO: (
        CampaignState.targeting_age_to,
        'новый максимальный возраст, для которого предназначена',
    ),
    CampaignEditActions.TARGETING_LOCATION: (
        CampaignState.targeting_location,
        'новую локацию, для которого предназначена',
    ),
}


@router.callback_query(CampaignEdit.filter(F.action == CampaignEditActions.DONE))
async def done_edit(
    call: CallbackQuery, callback_data: CampaignEdit, user: TelegramUsers
) -> None:
    await send_list(
        message=call.message,
        user=user,
        page=callback_data.page,
        campaign_id=callback_data.campaign_id,
        edit_text=True,
    )
    await call.answer()


@router.callback_query(CampaignEdit.filter(F.action == CampaignEditActions.BACK))
async def back_edit(call: CallbackQuery, callback_data: CampaignEdit) -> None:
    await send_edit_categories(
        message=call.message,
        page=callback_data.page,
        campaign_id=callback_data.campaign_id,
    )
    await call.answer()


@router.callback_query(CampaignEdit.filter(F.action.in_(MENU_ACTIONS.keys())))
async def change_menu(call: CallbackQuery, callback_data: CampaignEdit) -> None:
    menu_data = MENU_ACTIONS[callback_data.action]
    with suppress(TelegramBadRequest):
        await call.message.edit_text(
            text=menu_data[0],
            reply_markup=menu_data[1](callback_data.campaign_id, callback_data.page),
        )
    await call.answer()


@router.callback_query(CampaignEdit.filter(F.action.in_(EDIT_ACTIONS.keys())))
async def edit_field(
    call: CallbackQuery,
    callback_data: CampaignEdit,
    state: FSMContext,
    user: TelegramUsers,
) -> None:
    edit_data = EDIT_ACTIONS[callback_data.action]

    try:
        campaign_data = await api_client.get_campaign(
            advertiser_id=user.advertiser.id, campaign_id=callback_data.campaign_id
        )
    except:
        await call.message.edit_text(text='Кампания не найдена')
        await call.message.delete_reply_markup()
        return

    await state.set_state(edit_data[0])
    await state.update_data(
        action='edit',
        campaign=str(callback_data.campaign_id),
        page=callback_data.page,
        **campaign_data.model_dump(
            exclude={'targeting', 'advertiser_id', 'campaign_id'}
        ),
        **{
            f"targeting_{k}": v for k, v in campaign_data.targeting.model_dump().items()
        },
    )

    reply_kb = edit_data[2] if len(edit_data) == 3 else cancel_kb
    await call.message.answer(
        text=f"Отправьте {edit_data[1]} рекламной кампании", reply_markup=reply_kb
    )
    await call.answer()
