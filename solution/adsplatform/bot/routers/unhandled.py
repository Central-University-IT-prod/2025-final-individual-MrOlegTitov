from ..keyboards.reply import main_kb
from ..middlewares.user import UserMiddleware

from aiogram import Router
from aiogram.types import Message

router = Router()
router.message.middleware(UserMiddleware())


@router.message()
async def unhandled(message: Message) -> None:
    await message.answer(
        text='Я вас не понимаю. Пожалуйста, выберите желаемое действие',
        reply_markup=main_kb,
    )
