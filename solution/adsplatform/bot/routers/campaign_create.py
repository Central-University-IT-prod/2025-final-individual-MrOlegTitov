import uuid
from .campaign_list import send_edit_categories
from .. import api_client
from ..keyboards.reply import cancel_skip_kb, cancel_kb, targeting_gender_kb, main_kb
from ..middlewares.user import UserMiddleware
from ..states import CampaignState
from adsplatform.schemas.campaigns import TargetingGender
from adsplatform.db.models import TelegramUsers

from aiogram import Bot, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

router = Router()
router.message.middleware(UserMiddleware())


async def finish_edit(message: Message, state: FSMContext, user: TelegramUsers):
    try:
        data = await state.get_data()
        data['targeting'] = {
            'gender': data.get('targeting_gender'),
            'age_from': data.get('targeting_age_from'),
            'age_to': data.get('targeting_age_to'),
            'location': data.get('targeting_location'),
        }
        await api_client.update_campaign(
            advertiser_id=user.advertiser.id,
            campaign_id=str(await state.get_value('campaign')),
            data=data,
        )
    except Exception as e:
        await message.answer(
            text=f"Не удалось изменить данные рекламной кампании, по причине: "
            f"{str(e)}. Попробуйте ещё раз или отмените редактирование"
        )
        return

    state_data = await state.get_data()
    await state.clear()

    await message.answer(
        text='Данные рекламной кампании были успешно изменены', reply_markup=main_kb
    )
    await send_edit_categories(
        message=message,
        page=state_data.get('page'),
        campaign_id=state_data.get('campaign'),
        edit_text=False,
    )


@router.message(F.text == '➕ Создать кампанию', StateFilter(None))
async def new_campaign(message: Message, state: FSMContext) -> None:
    await state.set_state(CampaignState.ad_title)
    await state.update_data(action='create')
    await message.answer(
        text='Укажите название рекламной кампании', reply_markup=cancel_kb
    )


@router.message(F.text == '❌ Отменить', StateFilter(CampaignState))
async def cancel(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    if data.get('action') == 'edit':
        await message.answer(
            text='Редактирование рекламной кампании было отменено', reply_markup=main_kb
        )
        await send_edit_categories(
            message=message,
            page=data.get('page'),
            campaign_id=data.get('campaign'),
            edit_text=False,
        )
        return

    await message.answer(
        text='Создание новой рекламной кампании было отменено', reply_markup=main_kb
    )


@router.message(CampaignState.ad_title)
async def set_ad_title(
    message: Message, state: FSMContext, user: TelegramUsers
) -> None:
    await state.update_data(ad_title=message.text)
    if (await state.get_value('action')) == 'edit':
        await finish_edit(user=user, message=message, state=state)
        return

    await state.set_state(CampaignState.ad_text)
    await message.answer('Отправьте текст рекламной кампании')


@router.message(CampaignState.ad_text)
async def set_ad_text(message: Message, state: FSMContext, user: TelegramUsers) -> None:
    await state.update_data(ad_text=message.text)
    if (await state.get_value('action')) == 'edit':
        await finish_edit(user=user, message=message, state=state)
        return

    await state.set_state(CampaignState.ad_image)
    await message.answer(
        text='Отправьте изображение рекламной кампании', reply_markup=cancel_skip_kb
    )


@router.message(CampaignState.ad_image, F.photo)
@router.message(CampaignState.ad_image, F.document)
async def set_ad_image(
    message: Message, state: FSMContext, bot: Bot, user: TelegramUsers
) -> None:
    mime_type = 'image/jpeg'
    file_extension = 'jpg'
    if message.document:
        mime_type = message.document.mime_type
        file_extension = (
            message.document.file_name.split('.')[-1]
            if message.document.file_name
            else file_extension
        )
        if mime_type is not None and not mime_type.startswith('image'):
            await message.answer(
                text='Пожалуйста, отправьте фото или файл с изображением, которое будет '
                'использовано в рекламной кампании',
                reply_markup=cancel_skip_kb,
            )
            return

        file = await bot.get_file(message.document.file_id)
    else:
        file = await bot.get_file(message.photo[-1].file_id)

    file_data = await bot.download_file(file.file_path)

    file_name = f"{uuid.uuid4()}.{file_extension}"
    try:
        await api_client.upload_s3_file(
            key=file_name, data=file_data.read(), content_type=mime_type
        )
    except Exception as e:
        await message.answer(
            text=f"Не удалось загрузить отправленное вами фото, по причине: {str(e)}. "
            f"Пожалуйста, попробуйте ещё раз"
        )
        return
    await state.update_data(ad_image=file_name)

    if (await state.get_value('action')) == 'edit':
        await finish_edit(user=user, message=message, state=state)
        return

    await state.set_state(CampaignState.start_date)
    await message.answer(
        text='Теперь укажите дату начала рекламной кампании', reply_markup=cancel_kb
    )


@router.message(CampaignState.ad_image)
async def skip_ad_image(message: Message, state: FSMContext) -> None:
    if message.text == '⏩ Пропустить':
        await state.set_state(CampaignState.start_date)
        await message.answer(
            text='Теперь укажите дату начала рекламной кампании',
            reply_markup=cancel_kb,
        )
        return

    await message.answer(
        text='Пожалуйста, отправьте фото или файл с изображением, которое будет '
        'использовано в рекламной кампании',
        reply_markup=cancel_skip_kb,
    )


@router.message(CampaignState.start_date)
async def set_ad_start_date(
    message: Message, state: FSMContext, user: TelegramUsers
) -> None:
    try:
        start_date = int(message.text)
    except ValueError:
        await message.answer('Пожалуйста, отправьте число')
        return

    if start_date < 0:
        await message.answer('Дата начала не может быть меньше нуля')
        return

    end_date = await state.get_value('end_date')
    if end_date is not None and start_date > end_date:
        await message.answer('Дата начала не может быть больше даты окончания')
        return

    await state.update_data(start_date=start_date)

    if (await state.get_value('action')) == 'edit':
        await finish_edit(user=user, message=message, state=state)
        return

    await state.set_state(CampaignState.end_date)
    await message.answer('Укажите дату окончания рекламной кампании')


@router.message(CampaignState.end_date)
async def set_ad_end_date(
    message: Message, state: FSMContext, user: TelegramUsers
) -> None:
    try:
        end_date = int(message.text)
    except ValueError:
        await message.answer('Пожалуйста, отправьте число')
        return

    if end_date < 0:
        await message.answer('Дата окончания не может быть меньше нуля')
        return

    start_date = await state.get_value('start_date')
    if start_date is not None and start_date > end_date:
        await message.answer('Дата окончания не может быть меньше даты начала')
        return

    await state.update_data(end_date=end_date)

    if (await state.get_value('action')) == 'edit':
        await finish_edit(user=user, message=message, state=state)
        return

    await state.set_state(CampaignState.impressions_limit)
    await message.answer('Спасибо! Укажите целевое число просмотров')


@router.message(CampaignState.impressions_limit)
async def set_ad_impressions_limit(
    message: Message,
    state: FSMContext,
    user: TelegramUsers,
) -> None:
    try:
        impressions_limit = int(message.text)
    except ValueError:
        await message.answer('Пожалуйста, отправьте число')
        return

    if impressions_limit <= 0:
        await message.answer('Целевое число просмотров должно быть больше нуля')
        return

    await state.update_data(impressions_limit=impressions_limit)

    if (await state.get_value('action')) == 'edit':
        await finish_edit(user=user, message=message, state=state)
        return

    await state.set_state(CampaignState.clicks_limit)
    await message.answer('Укажите целевое число кликов')


@router.message(CampaignState.clicks_limit)
async def set_ad_clicks_limit(
    message: Message, state: FSMContext, user: TelegramUsers
) -> None:
    try:
        clicks_limit = int(message.text)
    except ValueError:
        await message.answer('Пожалуйста, отправьте число')
        return

    if clicks_limit <= 0:
        await message.answer('Целевое число кликов должно быть больше нуля')
        return

    if clicks_limit > await state.get_value('impressions_limit'):
        await message.answer(
            'Целевое число кликов не должно превышать целевое число просмотров'
        )
        return

    await state.update_data(clicks_limit=clicks_limit)

    if (await state.get_value('action')) == 'edit':
        await finish_edit(user=user, message=message, state=state)
        return

    await state.set_state(CampaignState.cost_per_impression)
    await message.answer('Укажите стоимость одного просмотра')


@router.message(CampaignState.cost_per_impression)
async def set_ad_cost_per_impression(
    message: Message, state: FSMContext, user: TelegramUsers
) -> None:
    try:
        cost_per_impression = float(message.text)
    except ValueError:
        await message.answer('Пожалуйста, отправьте число')
        return

    if cost_per_impression <= 0:
        await message.answer('Стоимость одного просмотра должна быть больше нуля')
        return

    await state.update_data(cost_per_impression=cost_per_impression)

    if (await state.get_value('action')) == 'edit':
        await finish_edit(user=user, message=message, state=state)
        return

    await state.set_state(CampaignState.cost_per_click)
    await message.answer('Укажите стоимость одного перехода')


@router.message(CampaignState.cost_per_click)
async def set_ad_cost_per_click(
    message: Message, state: FSMContext, user: TelegramUsers
) -> None:
    try:
        cost_per_click = float(message.text)
    except ValueError:
        await message.answer('Пожалуйста, отправьте число')
        return

    if cost_per_click <= 0:
        await message.answer('Стоимость одного перехода должна быть больше нуля')
        return

    await state.update_data(cost_per_click=cost_per_click)

    if (await state.get_value('action')) == 'edit':
        await finish_edit(user=user, message=message, state=state)
        return

    await state.set_state(CampaignState.targeting_gender)
    await message.answer(
        text='Отлично! Осталось настроить параметры таргетинга. Укажите пол, для '
        'которого предназначена рекламная кампания',
        reply_markup=targeting_gender_kb,
    )


@router.message(CampaignState.targeting_gender)
async def set_ad_targeting_gender(
    message: Message, state: FSMContext, user: TelegramUsers
) -> None:
    if message.text == '⏩ Пропустить':
        await state.set_state(CampaignState.targeting_age_from)
        await message.answer(
            text='Укажите минимальный возраст (включительно), для которого '
            'предназначена кампания',
            reply_markup=cancel_skip_kb,
        )
        return

    answer_mapping = {
        'Мужской': TargetingGender.MALE,
        'Женский': TargetingGender.FEMALE,
        'Любой': TargetingGender.ALL,
    }
    gender = answer_mapping.get(message.text, None)
    if not gender:
        await message.answer(
            text='Пожалуйста, выберите один из доступных вариантов',
            reply_markup=targeting_gender_kb,
        )
        return

    await state.update_data(targeting_gender=gender.value)

    if (await state.get_value('action')) == 'edit':
        await finish_edit(user=user, message=message, state=state)
        return

    await state.set_state(CampaignState.targeting_age_from)
    await message.answer(
        text='Укажите минимальный возраст (включительно), для которого '
        'предназначена кампания',
        reply_markup=cancel_skip_kb,
    )


@router.message(CampaignState.targeting_age_from)
async def set_ad_targeting_age_from(
    message: Message, state: FSMContext, user: TelegramUsers
) -> None:
    if message.text == '⏩ Пропустить':
        await state.set_state(CampaignState.targeting_age_to)
        await message.answer(
            'Укажите максимальный возраст (включительно), для которого '
            'предназначена кампания'
        )
        return

    try:
        age_from = int(message.text)
    except ValueError:
        await message.answer('Пожалуйста, отправьте число')
        return

    if age_from < 0:
        await message.answer('Возраст не может быть меньше нуля')
        return

    age_to = await state.get_value('targeting_age_to')
    if age_to is not None and age_from > age_to:
        await message.answer(
            'Минимальный возраст не может быть больше, чем максимальный'
        )
        return

    await state.update_data(targeting_age_from=age_from)

    if (await state.get_value('action')) == 'edit':
        await finish_edit(user=user, message=message, state=state)
        return

    await state.set_state(CampaignState.targeting_age_to)
    await message.answer(
        'Укажите максимальный возраст (включительно), для которого '
        'предназначена кампания'
    )


@router.message(CampaignState.targeting_age_to)
async def set_ad_targeting_age_to(
    message: Message, state: FSMContext, user: TelegramUsers
) -> None:
    if message.text == '⏩ Пропустить':
        await state.set_state(CampaignState.targeting_location)
        await message.answer('Укажите локацию, для которой предназначена кампания')
        return

    try:
        age_to = int(message.text)
    except ValueError:
        await message.answer('Пожалуйста, отправьте число')
        return

    if age_to < 0:
        await message.answer('Возраст не может быть меньше нуля')
        return

    age_from = await state.get_value('targeting_age_from')
    if age_from is not None and age_to < age_from:
        await message.answer(
            'Максимальный возраст не может быть меньше, чем минимальный'
        )
        return

    await state.update_data(targeting_age_to=age_to)
    if (await state.get_value('action')) == 'edit':
        await finish_edit(user=user, message=message, state=state)
        return

    await state.set_state(CampaignState.targeting_location)
    await message.answer('Укажите локацию, для которой предназначена кампания')


@router.message(CampaignState.targeting_location)
async def set_ad_targeting_location(
    message: Message, state: FSMContext, user: TelegramUsers
) -> None:
    if 'пропустить' not in message.text.lower():
        await state.update_data(targeting_location=message.text)

        if (await state.get_value('action')) == 'edit':
            await finish_edit(user=user, message=message, state=state)
            return

    try:
        data = await state.get_data()
        data['targeting'] = {
            'gender': data.get('targeting_gender'),
            'age_from': data.get('targeting_age_from'),
            'age_to': data.get('targeting_age_to'),
            'location': data.get('targeting_location'),
        }
        await api_client.create_campaign(advertiser_id=user.advertiser.id, data=data)
    except Exception as e:
        await state.clear()
        await message.answer(
            text=f"При создании компании, возникла ошибка: {str(e)}. Попробуйте ещё раз",
            reply_markup=main_kb,
        )
        return

    await state.clear()
    await message.answer(
        text='Вы успешно создали новую рекламную кампанию!',
        reply_markup=main_kb,
    )
