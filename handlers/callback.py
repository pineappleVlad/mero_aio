from datetime import datetime

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from telegram_bot_calendar import DetailedTelegramCalendar

from database.orm import adv_orm, user_orm, session_orm
from database.db_connection import get_session
from keyboards.inline import skip_keyboard, calendar_key_keyboard, hedings_keyboard
from utils.states import MainStates
from utils.data import DAYS_LOCALE, MONTHS_LOCALE, OTHER_HASHTAGS, MONTHS_LOCALE_FOR_HASHTAG, BASE_HEADING_HASHTAGS, CHANNEL_IDS_LONG, CHANNEL_IDS_SHORT
from utils.send_to_channel import send_to_channel


async def city_handler(call: CallbackQuery, bot: Bot, state: FSMContext):
    city = call.data
    chat_id = call.message.chat.id
    async with get_session() as db:
        check_user = await user_orm.get_user(chat_id, db)
        if not check_user:
            await user_orm.create_user(city=city, chat_id=chat_id, db=db)

        created_adv = await adv_orm.create_starting_adv(city_publish=city, db=db)
        check_bind = await session_orm.bind_exists(chat_id, created_adv.id, db)
        if not check_bind:
            await session_orm.bind_user_session(chat_id, created_adv.id, db)

    await state.set_state(MainStates.photo_input)
    await call.message.answer(text=f"""
Вы выбрали город {city} \n
➕ <strong> Прикрепите фото </strong> вашего мероприятия. Лучше если фото будет 
квадратным, это наиболее подходящие габариты изображения. \n \n
Если у вас публикация без изображения, нажмите 'Пропустить' \n \n
Для того, чтобы вернуться к выбору города нажмите /cancel
    """, parse_mode="HTML", reply_markup=skip_keyboard())
    await call.message.delete()


async def photo_handler_skip(call: CallbackQuery, bot: Bot, state: FSMContext):
    async with get_session() as db:
        if call.data == "skip":
            await call.message.delete()
            await call.message.answer(text="Ввод изображения пропущен")
            adv_id = await session_orm.get_adv_id(call.message.chat.id, db)
            await adv_orm.update_adv(adv_id, db, **{"photo": "skip"})
            await call.message.answer(text=f"""
<strong> Введите тему мероприятия. </strong>  
Это может быть бизнес форум, нетворкинг, 
фото-девичник, балет, выставка, научная 
конференция или даже бесплатная открытая 
встреча.

Пример: Балет в 2-х действиях 

Тема(вид) мероприятия всегда выделяется 
жирным, но вам её <strong> выделять жирным НЕ нужно </strong>  
Для того, чтобы начать ввод объявление заново нажмите /cancel
                        """, parse_mode="HTML")
            await state.set_state(MainStates.theme_input)


async def date_callback_handler(call: CallbackQuery, bot: Bot, state: FSMContext):
    result, key, step = DetailedTelegramCalendar(locale="ru").process(call.data)
    if not result and key:
        await bot.edit_message_text(f"Выберите дату",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=calendar_key_keyboard(key))
    elif result:
        await bot.edit_message_text(f"Вы выбрали {result}",
                              call.message.chat.id,
                              call.message.message_id)
        async with get_session() as db:
            adv_id = await session_orm.get_adv_id(call.message.chat.id, db)

            date_res = datetime.strptime(str(result), "%Y-%m-%d")
            year = str(int(date_res.strftime("%Y-%m-%d").split("-")[0]) % 100)
            date_string = date_res.strftime("%d %B %A").split(" ")
            day, month, day_of_week = date_string[0], MONTHS_LOCALE[date_string[1]], DAYS_LOCALE[date_string[2]]
            month_for_hashtag = MONTHS_LOCALE_FOR_HASHTAG[date_string[1]]
            output_date = f"{day} {month} ({day_of_week})"
            day_and_month = f"{month_for_hashtag}{day}"

            await adv_orm.update_adv(adv_id, db, **{"day_and_month": day_and_month})
            await adv_orm.add_hashtag(adv_id, f"#{month_for_hashtag}_{day}_{year}", db)
            await adv_orm.update_adv(adv_id, db, **{"date": output_date})
            await adv_orm.current_adv_state(adv_id, bot, call.message, db, state)
            await call.message.answer(text=f"""
**Введите время** мероприятия
Примеры: `Начало в 18:00`
или "С 15:00 до 18:00"

`9:00`  `10:00`  `11:00`  `12:00`
`13:00`  `14:00`  `15:00`  `16:00`
`17:00`  `18:00`  `19:00`  `20:00`
`21:00`  `22:00`  `23:00`  `00:00`

Тапните на время, чтобы скопировать.""", parse_mode="Markdown")
            await state.set_state(MainStates.time_input)


async def offer_handler_skip(call: CallbackQuery, bot: Bot, state: FSMContext):
    async with get_session() as db:
        if call.data == "skip":
            await call.message.delete()
            await call.message.answer(text="Ввод оффера пропущен")
            adv_id = await session_orm.get_adv_id(call.message.chat.id, db)
            await adv_orm.update_adv(adv_id, db, **{"offer": "skip"})
            await call.message.answer(text=f"""
<strong>Выберите рубрику</strong> для размещения в Mero.
Рубрика - это тема в группе Mero
            """, parse_mode="HTML", reply_markup=hedings_keyboard())
            await state.set_state(MainStates.heading_input)


async def heading_handler(call: CallbackQuery, bot: Bot, state: FSMContext):
    heading = call.data
    async with get_session() as db:
        await call.message.delete()
        adv_id = await session_orm.get_adv_id(call.message.chat.id, db)
        await adv_orm.update_adv(adv_id, db, **{"heading": heading})

        unittags = OTHER_HASHTAGS[call.data]
        modified_hashtags = ['`' + hashtag + '`' for hashtag in unittags]
        reccomend_hashtag = '\n'.join(modified_hashtags)

        day_for_hash = await adv_orm.get_day_for_hash(adv_id, db)
        base_hashtag = BASE_HEADING_HASHTAGS[heading]
        if base_hashtag[-1] == " ":
            base_hashtag = base_hashtag[:-1]
        base_hash_with_date = base_hashtag + "_" + day_for_hash

        await adv_orm.add_hashtag(adv_id, base_hashtag, db)
        await adv_orm.add_hashtag(adv_id, base_hash_with_date, db)
        await call.message.answer(text=f"""
Вы выбрали рубрику: {call.data}
Для навигации по приложению мы используем хэштеги
**Введите хэштеги** мероприятия через пробел (запятые между хэштегами ставить не нужно)
Рекомендуемые хэштеги в рубрике {call.data}:
{reccomend_hashtag}
                                  
Для того, чтобы скопировать хэштег, просто тапните по нему
Считаете, что в рубрике необходим хэштег? Напишите админу об этом
        """, parse_mode="Markdown")
        await state.set_state(MainStates.hashtags_input)


async def send_result_to_channel(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.message.delete()
    async with get_session() as db:
        adv_id = await session_orm.get_adv_id(call.message.chat.id, db)
        adv = await adv_orm.get_adv(adv_id, db)
        id_long = CHANNEL_IDS_LONG[adv.city_publish]
        id_short = CHANNEL_IDS_SHORT[adv.city_publish]
        try:
            await send_to_channel(adv, id_long, "long", bot)
            await send_to_channel(adv, id_short, "short", bot)
        except Exception:
            await call.message.answer(text="Неизвестная ошибка, попробуйте ввести объявление заново или написать админу")
        finally:
            await state.set_state(MainStates.start)


