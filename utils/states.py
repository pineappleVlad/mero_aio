from aiogram.fsm.state import StatesGroup, State


class MainStates(StatesGroup):
    start = State()
    cancel = State()
    choose_city = State()
    theme_input = State()
    name_input = State()
    photo_input = State()
    date_input = State()
    time_input = State()
    member_count_input = State()
    offer_input = State()
    heading_input = State()
    hashtags_input = State()
    description_input = State()
    address_input = State()
    price_input = State()
    url_input = State()
    all_right_check = State()