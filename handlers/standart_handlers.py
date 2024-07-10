from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from database.orm import adv_orm, user_orm, session_orm
from database.db_connection import get_session
from keyboards.inline import calendar_keyboard, skip_keyboard, hedings_keyboard, check_result_keyboard
from utils.states import MainStates

async def other_handler(message: Message, bot: Bot, state: FSMContext):
    await message.answer(text="Неизвестный ввод, если хотите начать заполнение объявления, "
                              "напишите /start")

async def photo_handler(message: Message, bot: Bot, state: FSMContext):
    photo = message.photo
    if not photo:
        await message.answer(text="Некорректный формат, отправьте фото")
        await state.set_state(MainStates.photo_input)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    else:
        photo = photo[-1].file_id
        async with get_session() as db:
            adv_id = await session_orm.get_adv_id(message.chat.id, db)
            await adv_orm.update_adv(adv_id, db, **{"photo": photo})
            await message.answer(text=f"""
<strong> Введите тему мероприятия. </strong>  
Это может быть бизнес форум, нетворкинг, 
фото-девичник, балет, выставка, научная 
конференция или даже бесплатная открытая 
встреча. \n
 
Пример: Балет в 2-х действиях \n 
 
Тема(вид) мероприятия всегда выделяется 
жирным, но вам её <strong> выделять жирным НЕ нужно </strong>  
Для того, чтобы начать ввод объявление заново нажмите /cancel
            """, parse_mode="HTML")
            await state.set_state(MainStates.theme_input)

async def theme_handler(message: Message, bot: Bot, state: FSMContext):
    theme_adv = message.text
    async with get_session() as db:
        adv_id = await session_orm.get_adv_id(message.chat.id, db)
        await adv_orm.update_adv(adv_id, db, **{"theme": theme_adv})
        await adv_orm.update_adv(adv_id, db, **{"tg_name_owner": message.from_user.username})
        await message.answer(text=f"""
Введите <strong>название мероприятия</strong>. Кавычки не нужны! \n 
Для того, чтобы начать ввод объявление заново нажмите /cancel
        """, parse_mode="HTML")
        await state.set_state(MainStates.name_input)

async def name_handler(message: Message, bot: Bot, state: FSMContext):
    name_adv = message.text
    async with get_session() as db:
        adv_id = await session_orm.get_adv_id(message.chat.id, db)
        await adv_orm.update_adv(adv_id, db, **{"name": name_adv})
        try:
            await adv_orm.current_adv_state(adv_id, bot, message, db, state)
        except ValueError:
            return
        await message.answer(text=f"""
Теперь заполним конкретику по нашему мероприятию \n 
<strong>Введите дату </strong> начала мероприятия
        """, parse_mode="HTML", reply_markup=calendar_keyboard())
        await state.set_state(MainStates.date_input)


async def time_handler(message: Message, bot: Bot, state: FSMContext):
    time_adv = message.text
    async with get_session() as db:
        adv_id = await session_orm.get_adv_id(message.chat.id, db)
        await adv_orm.update_adv(adv_id, db, **{"time": time_adv})
        try:
            await adv_orm.current_adv_state(adv_id, bot, message, db, state)
        except ValueError:
            return
        await message.answer(text=f"""
Введите <strong> количество участников </strong>

Если количество неизвестно, то поставьте "-"
        """, parse_mode="HTML")
        await state.set_state(MainStates.member_count_input)


async def people_count_handler(message: Message, bot: Bot, state: FSMContext):
    people_count = message.text
    async with get_session() as db:
        adv_id = await session_orm.get_adv_id(message.chat.id, db)
        try:
            if int(people_count) > 50:
                await adv_orm.add_hashtag(adv_id, "#BiG", db)
                day = await adv_orm.get_day_for_hash(adv_id, db)
                await adv_orm.add_hashtag(adv_id, f"#Big_{day}")
        except Exception:
            pass
        await adv_orm.update_adv(adv_id, db, **{"members_count": people_count})
        try:
            await adv_orm.current_adv_state(adv_id, bot, message, db, state)
        except ValueError:
            return
        await message.answer(text=f"""
<strong>Введите адрес</strong> мероприятия
Вы можете вставить ссылку на 2Гис или
Я-карты с адресом вашего мероприятия, но её
необходимо вшить в текст

Для того, чтобы начать ввод объявления заново нажмите /cancel
        """, parse_mode="HTML")
        await state.set_state(MainStates.address_input)


async def address_handler(message: Message, bot: Bot, state: FSMContext):
    address = message.text
    async with get_session() as db:
        adv_id = await session_orm.get_adv_id(message.chat.id, db)
        await adv_orm.update_adv(adv_id, db, **{"address": address})
        try:
            await adv_orm.current_adv_state(adv_id, bot, message, db, state)
        except ValueError:
            return
        await message.answer(text=f"""
<strong>Введите цену</strong> мероприятия,
также вы можете указать скидки и промокоды

Для того, чтобы начать ввод объявления заново нажмите /cancel
        """, parse_mode="HTML")
        await state.set_state(MainStates.price_input)

async def price_handler(message: Message, bot: Bot, state: FSMContext):
    price = message.text
    async with get_session() as db:
        adv_id = await session_orm.get_adv_id(message.chat.id, db)
        await adv_orm.update_adv(adv_id, db, **{"price": price})
        try:
            await adv_orm.current_adv_state(adv_id, bot, message, db, state)
        except ValueError:
            return
        await message.answer(text=f"""
<strong>Введите описание</strong> (максимум 710 символов)        
        """, parse_mode="HTML")
        await state.set_state(MainStates.description_input)

async def description_handler(message: Message, bot: Bot, state: FSMContext):
    description = message.text
    if len(description) > 710:
        await message.answer(text="Слишком длинное описание, введите заново")
        await state.set_state(MainStates.description_input)

    async with get_session() as db:
        adv_id = await session_orm.get_adv_id(message.chat.id, db)
        await adv_orm.update_adv(adv_id, db, **{"description": description})
        try:
            await adv_orm.current_adv_state(adv_id, bot, message, db, state)
        except ValueError:
            return
        await message.answer(text=f"""
<strong>Введите оффер </strong> (необязательно):
Оффер - это предложение(сильное
предложение), стимулирующее к тому
чтобы узнать о вашем мероприятии подробнее

Для того, чтобы начать ввод объявления заново нажмите /cancel
        """, parse_mode="HTML", reply_markup=skip_keyboard())
        await state.set_state(MainStates.offer_input)


async def offer_handler(message: Message, bot: Bot, state: FSMContext):
    offer = message.text
    async with get_session() as db:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        adv_id = await session_orm.get_adv_id(message.chat.id, db)
        await adv_orm.update_adv(adv_id, db, **{"offer": offer})
        try:
            await adv_orm.current_adv_state(adv_id, bot, message, db, state)
        except ValueError:
            return
        await message.answer(text=f"""
<strong>Выберите рубрику</strong> для размещения в Mero.
Рубрика - это тема в группе Mero
        """, parse_mode="HTML", reply_markup=hedings_keyboard())
        await state.set_state(MainStates.heading_input)


async def hashtags_handler(message: Message, bot: Bot, state: FSMContext):
    hashtags = message.text
    if hashtags[0] != "#":
        await message.answer(text=f'Введите хэштеги с решеткой:\n'
                                  f'Пример: #biz #Psy #magic'
                             )
    else:
        async with get_session() as db:
            adv_id = await session_orm.get_adv_id(message.chat.id, db)
            await adv_orm.add_hashtag(adv_id, hashtags, db)
            hash_list = hashtags.split()
            hash_detail = await adv_orm.get_day_for_hash(adv_id, db)
            for hashtag in hash_list:
                hashtag += "_"
                hashtag += hash_detail
                await adv_orm.add_hashtag(adv_id, hashtag, db)
            try:
                await adv_orm.current_adv_state(adv_id, bot, message, db, state)
            except ValueError:
                return
            await message.answer(text="""
Укажите ссылку на регистрацию билетов,
это может быть сайт, лид форма, личка менеджера ТГ.
В приложении запрещены ссылки на ватсап чаты,
телеграм каналы и чаты (это реклама)
""")
            await state.set_state(MainStates.url_input)


async def url_handler(message: Message, bot: Bot, state: FSMContext):
    url = message.text
    async with get_session() as db:
        adv_id = await session_orm.get_adv_id(message.chat.id, db)
        adv = await adv_orm.update_adv(adv_id, db, **{"url_registration": url})
        try:
            await adv_orm.current_adv_state(adv_id, bot, message, db, state)
        except TelegramBadRequest:
            await message.answer(text="Нерабочая ссылка, попробуйте ввести ссылку заново")
            await state.set_state(MainStates.url_input)
            return
        await message.answer(text=f"""
Ваш объявление будет опубликовано в <strong>{adv.city_publish}</strong>  
В канале и группе приложения Mero4You после модерации Админом 
 
Проверьте, всё ли верно?
        """, parse_mode="HTML", reply_markup=check_result_keyboard())
        await state.set_state(MainStates.all_right_check)

