from aiogram.fsm.state import StatesGroup, State


class LoginState(StatesGroup):
    action = State()  # register or login

    advertiser_id = State()  # Only for logining in
    advertiser_name = State()  # Only for registration


class CampaignState(StatesGroup):
    action = State()  # create | edit
    campaign = State()  # Used for editing
    page = State()  # Used for editing

    ad_title = State()
    ad_text = State()
    ad_image = State()

    start_date = State()
    end_date = State()

    impressions_limit = State()
    clicks_limit = State()
    cost_per_impression = State()
    cost_per_click = State()

    targeting_gender = State()
    targeting_age_from = State()
    targeting_age_to = State()
    targeting_location = State()
