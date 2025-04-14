from .. import api_client
from ..keyboards.fabric import (
    CampaignsList,
    CampaignListActions,
    campaigns_list_kb,
    campaign_deletion_kb,
    campaign_edit_menu_kb,
    total_statistics_kb,
)
from ..middlewares.user import UserMiddleware
from ..utils import serialize_campaign, serialize_statistics
from adsplatform.db.models import TelegramUsers
from contextlib import suppress
from uuid import UUID

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

router = Router()
router.message.middleware(UserMiddleware())
router.callback_query.middleware(UserMiddleware())


async def send_list(
    message: Message,
    user: TelegramUsers,
    page: int,
    campaign_id: UUID | str | None = None,
    edit_text: bool = False,
) -> None:
    if page == -1:
        campaigns = await api_client.list_campaigns(
            advertiser_id=str(user.advertiser.id),
        )
        page = max(len(campaigns) - 1, 0)
    else:
        if campaign_id is None:
            campaigns = await api_client.list_campaigns(
                advertiser_id=str(user.advertiser.id), page=page, size=1
            )
            if not campaigns and page > 0:
                return await send_list(
                    message=message,
                    user=user,
                    page=0,
                    campaign_id=None,
                    edit_text=edit_text,
                )
        else:
            try:
                campaigns = [
                    await api_client.get_campaign(
                        advertiser_id=str(user.advertiser.id),
                        campaign_id=str(campaign_id),
                    )
                ]
            except:
                return await send_list(
                    message=message,
                    user=user,
                    page=page,
                    campaign_id=None,
                    edit_text=edit_text,
                )
    if not campaigns:
        if not edit_text:
            await message.answer('Вы ещё не создали ни одной кампании')
        else:
            with suppress(TelegramBadRequest):
                await message.edit_text(text='Вы ещё не создали ни одной кампании')
                await message.delete_reply_markup()
        return

    campaign = campaigns[-1]
    text = serialize_campaign(campaign)
    markup = campaigns_list_kb(campaign_id=campaign.campaign_id, page=page)

    if edit_text:
        with suppress(TelegramBadRequest):
            await message.edit_text(
                text=text,
                reply_markup=markup,
            )
    else:
        await message.answer(
            text=text,
            reply_markup=markup,
        )


async def send_statistics(
    message: Message,
    page: int,
    campaign_id: UUID | str,
    week: int | None = None,
) -> None:
    try:
        campaign_stats = await api_client.get_campaign_stats(
            campaign_id=str(campaign_id)
        )
    except:
        with suppress(TelegramBadRequest):
            await message.edit_text(text='Рекламная кампания не найдена')
            await message.delete_reply_markup()
        return

    text = serialize_statistics(stats=campaign_stats, is_advertiser=False)
    with suppress(TelegramBadRequest):
        await message.edit_text(
            text=text,
            reply_markup=total_statistics_kb(
                campaign_id=campaign_id, page=page, week=week
            ),
        )


async def send_edit_categories(
    message: Message, page: int, campaign_id: UUID | str, edit_text: bool = True
) -> None:
    if edit_text:
        with suppress(TelegramBadRequest):
            await message.edit_text(
                text='Выберите категорию для редактирования, используя клавиатуру ниже.\n'
                '<i>Здесь вы можете изменить основную информацию, даты кампании, целевые '
                'значения или настройки таргетинга.</i>',
                reply_markup=campaign_edit_menu_kb(
                    campaign_id=campaign_id,
                    page=page,
                ),
            )
    else:
        await message.answer(
            text='Выберите категорию для редактирования, используя клавиатуру ниже.\n'
            '<i>Здесь вы можете изменить основную информацию, даты кампании, целевые '
            'значения или настройки таргетинга.</i>',
            reply_markup=campaign_edit_menu_kb(
                campaign_id=campaign_id,
                page=page,
            ),
        )


async def send_confirmation(
    message: Message,
    page: int,
    campaign_id: UUID | str,
) -> None:
    with suppress(TelegramBadRequest):
        await message.edit_text(
            text='❌ <b>Подтверждение удаления</b>\n'
            '⚠ <i>Вы уверены, что хотите удалить эту рекламную кампанию?</i>\n'
            'Это действие ❗ <b>невозможно отменить</b> ❗\n',
            reply_markup=campaign_deletion_kb(
                campaign_id=campaign_id,
                page=page,
            ),
        )


@router.message(F.text == '📋 Мои кампании', StateFilter(None))
async def list_campaigns(message: Message, user: TelegramUsers) -> None:
    await send_list(
        message=message,
        user=user,
        page=0,
        campaign_id=None,
        edit_text=False,
    )


@router.callback_query(CampaignsList.filter(F.action == CampaignListActions.NEXT))
async def next_page(
    call: CallbackQuery, callback_data: CampaignsList, user: TelegramUsers
) -> None:
    page = callback_data.page + 1
    await send_list(
        message=call.message,
        user=user,
        page=page,
        campaign_id=None,
        edit_text=True,
    )
    await call.answer()


@router.callback_query(CampaignsList.filter(F.action == CampaignListActions.PREVIOUS))
async def prev_page(
    call: CallbackQuery, callback_data: CampaignsList, user: TelegramUsers
) -> None:
    page = max(callback_data.page - 1, -1)
    await send_list(
        message=call.message,
        user=user,
        page=page,
        campaign_id=None,
        edit_text=True,
    )
    await call.answer()


@router.callback_query(CampaignsList.filter(F.action == CampaignListActions.STATISTICS))
async def campaign_statistics(
    call: CallbackQuery, callback_data: CampaignsList
) -> None:
    await send_statistics(
        message=call.message,
        campaign_id=callback_data.campaign_id,
        page=callback_data.page,
    )
    await call.answer()


@router.callback_query(CampaignsList.filter(F.action == CampaignListActions.EDIT))
async def edit_campaign(call: CallbackQuery, callback_data: CampaignsList) -> None:
    await send_edit_categories(
        message=call.message,
        campaign_id=callback_data.campaign_id,
        page=callback_data.page,
    )
    await call.answer()


@router.callback_query(CampaignsList.filter(F.action == CampaignListActions.DELETE))
async def delete_campaign(call: CallbackQuery, callback_data: CampaignsList) -> None:
    await send_confirmation(
        message=call.message,
        campaign_id=callback_data.campaign_id,
        page=callback_data.page,
    )
    await call.answer()
