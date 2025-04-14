from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

login_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='✅ Зарегистрироваться')],
        [KeyboardButton(text='🔑 Войти в аккаунт')],
    ],
    input_field_placeholder='Выберите действие',
    resize_keyboard=True,
    one_time_keyboard=False,
    selective=True,
)

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='➕ Создать кампанию'),
            KeyboardButton(text='📋 Мои кампании'),
        ],
        [
            KeyboardButton(text='📊 Моя статистика'),
        ],
    ],
    input_field_placeholder='Выберите желаемое действие',
    resize_keyboard=True,
    one_time_keyboard=True,
    selective=True,
)

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='❌ Отменить')]],
    resize_keyboard=True,
    one_time_keyboard=True,
    selective=True,
)

cancel_skip_kb = cancel_kb.model_copy(
    update={
        'keyboard': [cancel_kb.keyboard[0], [KeyboardButton(text='⏩ Пропустить')]],
        'one_time_keyboard': False,
    }
)

targeting_gender_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Мужской'),
            KeyboardButton(text='Женский'),
            KeyboardButton(text='Любой'),
        ],
        [
            KeyboardButton(text='⏩ Пропустить'),
            KeyboardButton(text='❌ Отменить'),
        ],
    ],
    input_field_placeholder='Укажите пол',
    resize_keyboard=True,
    one_time_keyboard=True,
    selective=True,
)
targeting_gender_edit_kb = targeting_gender_kb.model_copy(
    update={
        'keyboard': [
            targeting_gender_kb.keyboard[0],
            targeting_gender_kb.keyboard[1][1:],
        ]
    }
)
