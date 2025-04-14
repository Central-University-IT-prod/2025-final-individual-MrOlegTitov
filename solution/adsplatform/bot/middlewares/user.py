from adsplatform.db.models import TelegramUsers
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery


class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        message = event if isinstance(event, Message) else event.message

        user = await TelegramUsers.get_or_none(
            telegram_id=event.from_user.id
        ).prefetch_related('advertiser')
        if not user:
            return await message.answer(text='Чтобы начать, отправьте мне /start')

        data['user'] = user
        return await handler(event, data)
