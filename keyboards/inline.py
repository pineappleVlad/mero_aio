import json
from typing import Any

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from telegram_bot_calendar import DetailedTelegramCalendar


def url_keyboard(url: str) -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text="Регистрация", url=url, callback_data="go_to_url")
    return keyboard_builder.as_markup()


def city_keyboard() -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text="Москва", callback_data="Москва")
    keyboard_builder.button(text="Санкт-Петербург", callback_data="Санкт-Петербург")
    keyboard_builder.button(text="Новосибирск", callback_data="Новосибирск")
    keyboard_builder.button(text="Екатеринбург", callback_data="Екатеринбург")
    keyboard_builder.adjust(1, 1, 1, 1)
    return keyboard_builder.as_markup()


def check_result_keyboard() -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text="Опубликовать", callback_data="send_result")
    keyboard_builder.button(text="Создать объявление заново", callback_data="cancel")
    keyboard_builder.adjust(1, 1)
    return keyboard_builder.as_markup()


def skip_keyboard() -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text="Пропустить", callback_data="skip")
    return keyboard_builder.as_markup()


def hedings_keyboard() -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text="Бизнес", callback_data="Бизнес")
    keyboard_builder.button(text="Психология", callback_data="Психология")
    keyboard_builder.button(text="Эзотерические", callback_data="Эзотерические")
    keyboard_builder.button(text="Мужские", callback_data="Мужские")
    keyboard_builder.button(text="Женские", callback_data="Женские")
    keyboard_builder.button(text="Детские (с детьми)", callback_data="Детские (с детьми)")
    keyboard_builder.button(text="Образование/Тренинги/Обучение", callback_data="Образование/Тренинги/Обучение")
    keyboard_builder.button(text="Культура и искусство", callback_data="Культура и искусство")
    keyboard_builder.button(text="Музыкально-танцевальные", callback_data="Музыкально-танцевальные")
    keyboard_builder.button(text="Здоровье и спорт", callback_data="Здоровье и спорт")
    keyboard_builder.button(text="Настолки и дружеские встречи", callback_data="Настолки и дружеские встречи")
    keyboard_builder.button(text="Бесплатные", callback_data="Бесплатные")
    keyboard_builder.adjust(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
    return keyboard_builder.as_markup()


def calendar_keyboard() -> InlineKeyboardMarkup:
    calendar, step = DetailedTelegramCalendar(locale="ru").build()
    calendar_data = json.loads(calendar)

    for row in calendar_data['inline_keyboard']:
        for button in row:
            button['text'] = str(button['text'])

    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=button['text'], callback_data=button['callback_data']) for button in row]
        for row in calendar_data['inline_keyboard']
    ])

    return inline_keyboard

def calendar_key_keyboard(key: Any) -> InlineKeyboardMarkup:
    calendar_data = json.loads(key)
    for row in calendar_data['inline_keyboard']:
        for button in row:
            button['text'] = str(button['text'])

    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=button['text'], callback_data=button['callback_data']) for button in row]
        for row in calendar_data['inline_keyboard']
    ])

    return inline_keyboard



