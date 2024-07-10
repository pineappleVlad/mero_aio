import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ContentType
from aiogram.filters import Command
from utils.states import MainStates
from config import TOKEN
from handlers.command_handler import start, cancel, cancel_call
from handlers.standart_handlers import *
from handlers.callback import *
from database.db_connection import init_models


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    dp.message.register(start, Command('start'))
    dp.callback_query.register(cancel_call, F.data.startswith("cancel"))
    dp.message.register(cancel, Command('cancel'))

    dp.callback_query.register(city_handler, MainStates.choose_city)
    dp.callback_query.register(photo_handler_skip, MainStates.photo_input, F.data.startswith("skip"))
    dp.callback_query.register(offer_handler_skip, MainStates.offer_input, F.data.startswith("skip"))
    dp.callback_query.register(date_callback_handler, MainStates.date_input, DetailedTelegramCalendar.func())
    dp.callback_query.register(heading_handler, MainStates.heading_input)
    dp.callback_query.register(send_result_to_channel, MainStates.all_right_check, F.data.startswith("send_result"))


    dp.message.register(photo_handler, MainStates.photo_input, F.content_type == ContentType.PHOTO)
    dp.message.register(name_handler, MainStates.name_input, F.content_type == ContentType.TEXT)
    dp.message.register(theme_handler, MainStates.theme_input, F.content_type == ContentType.TEXT)
    dp.message.register(time_handler, MainStates.time_input, F.content_type == ContentType.TEXT)
    dp.message.register(people_count_handler, MainStates.member_count_input, F.content_type == ContentType.TEXT)
    dp.message.register(address_handler, MainStates.address_input, F.content_type == ContentType.TEXT)
    dp.message.register(price_handler, MainStates.price_input, F.content_type == ContentType.TEXT)
    dp.message.register(description_handler, MainStates.description_input, F.content_type == ContentType.TEXT)
    dp.message.register(offer_handler, MainStates.offer_input, F.content_type == ContentType.TEXT)
    dp.message.register(hashtags_handler, MainStates.hashtags_input, F.content_type == ContentType.TEXT)
    dp.message.register(url_handler, MainStates.url_input, F.content_type == ContentType.TEXT)

    dp.message.register(other_handler)
    try:

        await init_models()
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())