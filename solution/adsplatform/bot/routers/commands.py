from ..states import LoginState
from ..keyboards.reply import login_kb
from adsplatform.db.models import TelegramUsers

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    user = await TelegramUsers.get_or_none(telegram_id=message.from_user.id)
    if not user or not user.advertiser:
        await state.set_state(LoginState.action)
        await message.answer(
            text='👋 Привет! Это бот Ads Platform — он поможет вам управлять '
            'рекламными кампаниями прямо в Telegram.\n'
            'Вы можете:\n'
            '📢 Создавать и редактировать кампании\n'
            '📊 Следить за статистикой\n'
            '🎯 Настраивать таргетинг\n'
            'Выберите, с чего начать:\n'
            '✅ <b>Зарегистрироваться</b> – если у вас ещё нет аккаунта\n'
            '🔑 <b>Войти в аккаунт</b> – если у вас уже есть ID рекламодателя '
            'с нашей платформы',
            reply_markup=login_kb,
        )
        return
