from adsplatform.schemas.campaigns import Campaign, TargetingGender
from adsplatform.schemas.statistics import CampaignStats, CampaignDailyStats


AGE_MAPPINGS = {
    TargetingGender.MALE: 'мужской',
    TargetingGender.FEMALE: 'женский',
    TargetingGender.ALL: 'любой',
}


def serialize_campaign(campaign: Campaign) -> str:
    title = f"📢 <b>{campaign.ad_title}</b>"
    text = f"📝 Описание: {campaign.ad_text}"

    prices = (
        f"💰 Стоимости: {campaign.cost_per_impression} за просмотр"
        f", {campaign.cost_per_click} за переход"
    )
    limits = (
        f"🎯 Цели: {campaign.impressions_limit} просмотров"
        f", {campaign.clicks_limit} переходов"
    )

    dates = f"📆 Сроки: {campaign.start_date} - {campaign.end_date}"

    targeting_title = '🌍 Таргетинг:'
    targeting_gender = f"  • 🚻 Пол: {AGE_MAPPINGS.get(campaign.targeting.gender if campaign.targeting else None, 'не указан')}"
    targeting_age_from = (
        f"от {campaign.targeting.age_from}"
        if campaign.targeting and campaign.targeting.age_from
        else ''
    )
    targeting_age_to = (
        f"до {campaign.targeting.age_to}"
        if campaign.targeting and campaign.targeting.age_to
        else ''
    )
    targeting_age = (
        f"  • 🔢 Возраст: "
        f"{
            ', '.join(filter(lambda x: x, [targeting_age_from, targeting_age_to]))
            or 'не указан'
        }"
    )
    targeting_location = f"  • 📍 Локация: {(campaign.targeting.location or 'не указана') if campaign.targeting else 'не указана'}"

    return '\n'.join(
        [
            title,
            text,
            prices,
            limits,
            dates,
            targeting_title,
            targeting_gender,
            targeting_age,
            targeting_location,
        ]
    )


def serialize_statistics(stats: CampaignStats, is_advertiser: bool = False) -> str:
    title = (
        f"<b>📊 Статистика {'кампании' if not is_advertiser else 'рекламодателя'}</b>"
    )
    impressions = f"👁 Просмотры: {stats.impressions_count}"
    clicks = f"🔗 Переходы: {stats.clicks_count}"
    conversion = f"📈 Конверсия: {round(stats.conversion, 2)}%"
    spent_title = '💰 Расходы:'
    spent_impressions = f"  • 👁 На просмотры: {stats.spent_impressions}"
    spent_clicks = f"  • 🔗 На переходы: {stats.spent_clicks}"
    spent_total = f"  • 💵 Всего: {stats.spent_total}"

    return '\n'.join(
        [
            title,
            impressions,
            clicks,
            conversion,
            spent_title,
            spent_impressions,
            spent_clicks,
            spent_total,
        ]
    )


def serialize_daily_statistics(
    stats: list[CampaignDailyStats],
    start_date: int,
    end_date: int,
    is_advertiser: bool = False,
) -> str:
    title = (
        f"📊 <b>Статистика {'кампании' if not is_advertiser else 'рекламодателя'} "
        f"за неделю</b>"
    )
    dates = f"🗓 С {start_date} по {end_date}"

    daily_data = [
        (
            f"📅 <b>День {day_stats.date}:</b>\n"
            f"👁 Просмотры: {day_stats.impressions_count} | "
            f"🔗 Переходы: {day_stats.clicks_count} | "
            f"💰 Расходы: {day_stats.spent_total}"
        )
        for day_stats in stats
    ]

    return '\n'.join([title, dates] + daily_data)
