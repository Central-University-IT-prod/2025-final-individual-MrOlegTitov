from enum import Enum
from uuid import UUID

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class CampaignListActions(str, Enum):
    NEXT = 'N'
    PREVIOUS = 'P'
    STATISTICS = 'S'
    DELETE = 'D'
    EDIT = 'E'


class StatisticsActions(str, Enum):
    BACK = 'B'

    TOTAL = 'T'
    DAILY = 'D'

    NEXT = 'N'
    PREVIOUS = 'P'


class CampaignEditActions(str, Enum):
    # Menu
    DONE = 'DONE'  # Back to list
    BACK = 'BACK'  # Back to categories menu

    # Editing Categories
    INFO = 'INFO'
    DATES = 'DATES'
    VALUES = 'VALUE'
    TARGETING = 'TARG'

    # Info
    AD_TITLE = 'TITLE'
    AD_TEXT = 'TEXT'
    AD_IMAGE = 'IMAGE'

    # Dates
    START_DATE = 'ST_DT'
    END_DATE = 'ED_DT'

    # Limits/prices
    IMPRESSIONS_LIMIT = 'I_LIM'
    CLICKS_LIMIT = 'C_LIM'
    COST_PER_IMPRESSION = 'C_P_I'
    COST_PER_CLICK = 'C_P_C'

    # Targeting
    TARGETING_GENDER = 'T_GND'
    TARGETING_AGE_FROM = 'T_A_F'
    TARGETING_AGE_TO = 'T_A_T'
    TARGETING_LOCATION = 'T_LOC'


class ConfirmationActions(str, Enum):
    YES = 'Y'
    NO = 'N'


class CampaignsList(CallbackData, prefix='cl'):
    action: CampaignListActions

    campaign_id: UUID
    page: int


class CampaignStatistics(CallbackData, prefix='cs'):
    action: StatisticsActions

    campaign_id: UUID
    page: int

    week: int | None = None


class AdvertiserStatistics(CallbackData, prefix='as'):
    action: StatisticsActions

    week: int | None = None


class CampaignEdit(CallbackData, prefix='ce'):
    action: CampaignEditActions

    campaign_id: UUID
    page: int


class CampaignDeletion(CallbackData, prefix='cd'):
    action: ConfirmationActions

    campaign_id: UUID
    page: int


def campaigns_list_kb(campaign_id: UUID, page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text='⬅️',
            callback_data=CampaignsList(
                action=CampaignListActions.PREVIOUS, page=page, campaign_id=campaign_id
            ).pack(),
        ),
        InlineKeyboardButton(
            text='📊 Статистика',
            callback_data=CampaignsList(
                action=CampaignListActions.STATISTICS,
                page=page,
                campaign_id=campaign_id,
            ).pack(),
        ),
        InlineKeyboardButton(
            text='➡️',
            callback_data=CampaignsList(
                action=CampaignListActions.NEXT, page=page, campaign_id=campaign_id
            ).pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text='📝 Редактировать',
            callback_data=CampaignsList(
                action=CampaignListActions.EDIT, page=page, campaign_id=campaign_id
            ).pack(),
        ),
        InlineKeyboardButton(
            text='❌ Удалить',
            callback_data=CampaignsList(
                action=CampaignListActions.DELETE, page=page, campaign_id=campaign_id
            ).pack(),
        ),
    )

    return builder.as_markup()


def total_statistics_kb(
    campaign_id: UUID | None = None, page: int | None = None, week: int | None = None
) -> InlineKeyboardMarkup:
    if campaign_id:
        if page is None:
            raise ValueError('Page must be specified for campaign statistics')
        base_data = CampaignStatistics(
            action=StatisticsActions.BACK,
            campaign_id=campaign_id,
            page=page,
            week=week,
        )
    else:
        base_data = AdvertiserStatistics(
            action=StatisticsActions.BACK,
            week=week,
        )
    builder = InlineKeyboardBuilder()
    (
        builder.row(
            InlineKeyboardButton(
                text='📆 Дневная',
                callback_data=base_data.model_copy(
                    update={'action': StatisticsActions.DAILY}
                ).pack(),
            ),
        ),
    )
    if campaign_id:
        builder.row(
            InlineKeyboardButton(
                text='⬅️ Назад',
                callback_data=base_data.pack(),
            ),
        )

    return builder.as_markup()


def daily_statistics_kb(
    week: int, page: int | None = None, campaign_id: UUID | None = None
) -> InlineKeyboardMarkup:
    if campaign_id:
        if page is None:
            raise ValueError('Page must be specified for campaign statistics')
        base_data = CampaignStatistics(
            action=StatisticsActions.BACK,
            campaign_id=campaign_id,
            page=page,
            week=week,
        )
    else:
        base_data = AdvertiserStatistics(
            action=StatisticsActions.BACK,
            week=week,
        )
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text='⬅️',
            callback_data=base_data.model_copy(
                update={'action': StatisticsActions.PREVIOUS}
            ).pack(),
        ),
        InlineKeyboardButton(
            text='📈 Общая',
            callback_data=base_data.model_copy(
                update={'action': StatisticsActions.TOTAL}
            ).pack(),
        ),
        InlineKeyboardButton(
            text='➡️',
            callback_data=base_data.model_copy(
                update={'action': StatisticsActions.NEXT}
            ).pack(),
        ),
    )
    if campaign_id:
        builder.row(
            InlineKeyboardButton(
                text='⬅️ Назад',
                callback_data=base_data.pack(),
            ),
        )

    return builder.as_markup()


def campaign_deletion_kb(campaign_id: UUID, page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text='❌ Отмена',
            callback_data=CampaignDeletion(
                campaign_id=campaign_id, page=page, action=ConfirmationActions.NO
            ).pack(),
        ),
        InlineKeyboardButton(
            text='✅ Подтвердить',
            callback_data=CampaignDeletion(
                campaign_id=campaign_id, page=page, action=ConfirmationActions.YES
            ).pack(),
        ),
    )

    return builder.as_markup()


def campaign_edit_menu_kb(campaign_id: UUID, page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text='📄 Основания информация',
            callback_data=CampaignEdit(
                campaign_id=campaign_id, page=page, action=CampaignEditActions.INFO
            ).pack(),
        ),
        InlineKeyboardButton(
            text='📆 Даты кампании',
            callback_data=CampaignEdit(
                campaign_id=campaign_id, page=page, action=CampaignEditActions.DATES
            ).pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text='🎯 Целевые значения',
            callback_data=CampaignEdit(
                campaign_id=campaign_id, page=page, action=CampaignEditActions.VALUES
            ).pack(),
        ),
        InlineKeyboardButton(
            text='🌍 Таргетинг',
            callback_data=CampaignEdit(
                campaign_id=campaign_id, page=page, action=CampaignEditActions.TARGETING
            ).pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text='✅ Завершить',
            callback_data=CampaignEdit(
                campaign_id=campaign_id, page=page, action=CampaignEditActions.DONE
            ).pack(),
        )
    )

    return builder.as_markup()


def campaign_edit_info_kb(campaign_id: UUID, page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text='✏️ Название',
            callback_data=CampaignEdit(
                campaign_id=campaign_id, page=page, action=CampaignEditActions.AD_TITLE
            ).pack(),
        ),
        InlineKeyboardButton(
            text='📝 Описание',
            callback_data=CampaignEdit(
                campaign_id=campaign_id, page=page, action=CampaignEditActions.AD_TEXT
            ).pack(),
        ),
        InlineKeyboardButton(
            text='🖼 Изображение',
            callback_data=CampaignEdit(
                campaign_id=campaign_id, page=page, action=CampaignEditActions.AD_IMAGE
            ).pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text='⬅️ Назад',
            callback_data=CampaignEdit(
                campaign_id=campaign_id, page=page, action=CampaignEditActions.BACK
            ).pack(),
        )
    )

    return builder.as_markup()


def campaign_edit_dates_kb(campaign_id: UUID, page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text='📆 Дата начала',
            callback_data=CampaignEdit(
                campaign_id=campaign_id,
                page=page,
                action=CampaignEditActions.START_DATE,
            ).pack(),
        ),
        InlineKeyboardButton(
            text='🏁 Дата окончания',
            callback_data=CampaignEdit(
                campaign_id=campaign_id, page=page, action=CampaignEditActions.END_DATE
            ).pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text='⬅️ Назад',
            callback_data=CampaignEdit(
                campaign_id=campaign_id, page=page, action=CampaignEditActions.BACK
            ).pack(),
        )
    )

    return builder.as_markup()


def campaign_edit_values_kb(campaign_id: UUID, page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text='🎯 Макс. кол-во просмотров',
            callback_data=CampaignEdit(
                campaign_id=campaign_id,
                page=page,
                action=CampaignEditActions.IMPRESSIONS_LIMIT,
            ).pack(),
        ),
        InlineKeyboardButton(
            text='🔗 Макс. кол-во переходов',
            callback_data=CampaignEdit(
                campaign_id=campaign_id,
                page=page,
                action=CampaignEditActions.CLICKS_LIMIT,
            ).pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text='💸 Цена одного просмотра',
            callback_data=CampaignEdit(
                campaign_id=campaign_id,
                page=page,
                action=CampaignEditActions.COST_PER_IMPRESSION,
            ).pack(),
        ),
        InlineKeyboardButton(
            text='💰 Цена одного перехода',
            callback_data=CampaignEdit(
                campaign_id=campaign_id,
                page=page,
                action=CampaignEditActions.COST_PER_CLICK,
            ).pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text='⬅️ Назад',
            callback_data=CampaignEdit(
                campaign_id=campaign_id, page=page, action=CampaignEditActions.BACK
            ).pack(),
        )
    )

    return builder.as_markup()


def campaign_edit_targeting_kb(campaign_id: UUID, page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text='🌍 Локация',
            callback_data=CampaignEdit(
                campaign_id=campaign_id,
                page=page,
                action=CampaignEditActions.TARGETING_LOCATION,
            ).pack(),
        ),
        InlineKeyboardButton(
            text='🚻 Пол',
            callback_data=CampaignEdit(
                campaign_id=campaign_id,
                page=page,
                action=CampaignEditActions.TARGETING_GENDER,
            ).pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text='👶 Минимальный возраст',
            callback_data=CampaignEdit(
                campaign_id=campaign_id,
                page=page,
                action=CampaignEditActions.TARGETING_AGE_FROM,
            ).pack(),
        ),
        InlineKeyboardButton(
            text='👴 Максимальный возраст',
            callback_data=CampaignEdit(
                campaign_id=campaign_id,
                page=page,
                action=CampaignEditActions.TARGETING_AGE_TO,
            ).pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text='⬅️ Назад',
            callback_data=CampaignEdit(
                campaign_id=campaign_id, page=page, action=CampaignEditActions.BACK
            ).pack(),
        )
    )

    return builder.as_markup()
