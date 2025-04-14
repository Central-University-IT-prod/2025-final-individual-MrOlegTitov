from ..states import LoginState
from ..keyboards.reply import main_kb, cancel_kb, login_kb
from adsplatform.db.models import TelegramUsers, Advertisers

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

router = Router()


async def finish_login(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text='Готово! ✅ Вы вошли в аккаунт рекламодателя. '
        'Теперь вы можете создавать и управлять своими кампаниями',
        reply_markup=main_kb,
    )


@router.message(F.text == '✅ Зарегистрироваться', LoginState.action)
async def register(message: Message, state: FSMContext) -> None:
    await state.set_state(LoginState.advertiser_name)
    await message.answer(
        text='Давайте создадим вам аккаунт рекламодателя! 🔥 Пожалуйста, введите '
        'название вашей компании или ваше имя, если вы рекламируетесь как '
        'частное лицо.',
        reply_markup=cancel_kb,
    )


@router.message(F.text == '🔑 Войти в аккаунт', LoginState.action)
async def login(message: Message, state: FSMContext) -> None:
    await state.set_state(LoginState.advertiser_id)
    await message.answer(
        text='Введите ваш ID рекламодателя, который вы получили на нашей платформе. '
        'Если у вас его нет, вы можете зарегистрироваться.',
        reply_markup=cancel_kb,
    )


@router.message(F.text == '❌ Отменить', StateFilter(LoginState))
async def cancel(message: Message, state: FSMContext) -> None:
    await state.set_state(LoginState.action)
    await message.answer(text='Выберите желаемый способ входа', reply_markup=login_kb)


@router.message(LoginState.advertiser_id)
async def login_advertiser_id(message: Message, state: FSMContext) -> None:
    try:
        advertiser = await Advertisers.get(id=message.text)
    except:
        await message.answer(
            text='Рекламодателя с указанным ID не существует. Убедитесь, что ввели '
            'верные данные, или создайте новый аккаунт'
        )
        return

    await TelegramUsers.create(
        telegram_id=message.from_user.id, chat_id=message.chat.id, advertiser=advertiser
    )
    await finish_login(message=message, state=state)


@router.message(LoginState.advertiser_name)
async def register_advertiser_name(message: Message, state: FSMContext) -> None:
    advertiser = await Advertisers.create(name=message.text)
    await TelegramUsers.create(
        telegram_id=message.from_user.id, chat_id=message.chat.id, advertiser=advertiser
    )
    await finish_login(message=message, state=state)
