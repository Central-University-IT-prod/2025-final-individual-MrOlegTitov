from .campaign_list import send_list
from .. import api_client
from ..keyboards.fabric import (
    CampaignDeletion,
    ConfirmationActions,
)
from ..middlewares.user import UserMiddleware
from adsplatform.db.models import TelegramUsers

from aiogram import F, Router
from aiogram.types import CallbackQuery

router = Router()
router.callback_query.middleware(UserMiddleware())


@router.callback_query(CampaignDeletion.filter(F.action == ConfirmationActions.NO))
async def cancel_deletion(
    call: CallbackQuery, callback_data: CampaignDeletion, user: TelegramUsers
) -> None:
    await send_list(
        message=call.message,
        user=user,
        page=callback_data.page,
        campaign_id=callback_data.campaign_id,
        edit_text=True,
    )
    await call.answer()


@router.callback_query(CampaignDeletion.filter(F.action == ConfirmationActions.YES))
async def confirm_deletion(
    call: CallbackQuery, callback_data: CampaignDeletion, user: TelegramUsers
) -> None:
    await api_client.delete_campaign(
        advertiser_id=str(user.advertiser.id),
        campaign_id=str(callback_data.campaign_id),
    )
    await send_list(
        message=call.message,
        user=user,
        page=0,
        campaign_id=None,
        edit_text=True,
    )
    await call.answer()
