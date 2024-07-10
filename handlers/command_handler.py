from aiogram import Bot
from aiogram.filters import state
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database.db_connection import get_session
from utils.commands import set_commands
from utils.states import MainStates
from keyboards.inline import city_keyboard
from database.orm import *


async def start(message: Message, bot: Bot, state: FSMContext):
    async with get_session() as db:
        adv_id = await session_orm.get_adv_id(message.chat.id, db)
        if adv_id:
            await adv_orm.delete_adv(adv_id, db)
            await session_orm.bind_delete(message.chat.id, db)

    await state.set_state(MainStates.start)
    await set_commands(bot)

    if message.message_id - 1:
        await bot.delete_message(message_id=(message.message_id - 1), chat_id=message.chat.id)

    await message.answer(text=f'<strong> Выберите город </strong> в котором хотите разместить объявление',
                         reply_markup=city_keyboard(), parse_mode="HTML")
    await state.set_state(MainStates.choose_city)


async def cancel(message: Message, bot: Bot, state: FSMContext):
    async with get_session() as db:
        await session_orm.bind_delete(message.chat.id, db)
    if message.message_id - 1:
        await bot.delete_message(message_id=(message.message_id - 1), chat_id=message.chat.id)
    await state.set_state(MainStates.cancel)
    await message.answer(text=f'Создание объявления отменено. Для создания нового напишите /start')

async def cancel_call(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.message.delete()
    async with get_session() as db:
        await session_orm.bind_delete(call.message.chat.id, db)
    await state.set_state(MainStates.cancel)
    await bot.send_message(text=f'Создание объявления отменено. Для создания нового напишите /start', chat_id=call.message.chat.id)