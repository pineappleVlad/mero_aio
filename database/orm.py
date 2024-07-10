from typing import Any

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.models import Users, Advertisements, CurrentSessions
from sqlalchemy import select, Date, Time, and_
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline import url_keyboard
from utils.states import MainStates


class UserOrm():
    async def create_user(self, city: str, chat_id: int, db: AsyncSession) -> Users:
        user = Users(city=city, chat_id=chat_id)
        db.add(user)
        await db.commit()
        return user

    async def get_user(self, chat_id: int, db: AsyncSession) -> Users:
        user_query = select(Users).where(Users.chat_id == chat_id)
        result = await db.execute(user_query)
        user = result.scalars().first()
        return user


class AdvOrm():
    async def create_starting_adv(self, city_publish: str, db: AsyncSession) -> Advertisements:
        adv = Advertisements(city_publish=city_publish)
        db.add(adv)
        await db.commit()
        return adv

    async def get_adv(self, adv_id: int, db: AsyncSession) -> Advertisements:
        adv_query = select(Advertisements).where(Advertisements.id == adv_id)
        result = await db.execute(adv_query)
        adv = result.scalars().first()
        return adv

    async def delete_adv(self, adv_id: int, db: AsyncSession) -> bool:
        adv = await self.get_adv(adv_id=adv_id, db=db)
        if adv:
            await db.delete(adv)
            await db.commit()
            return True
        else:
            return False

    async def update_adv(self, adv_id: int, db: AsyncSession, **kwargs: dict) -> Advertisements:
        adv = await self.get_adv(adv_id=adv_id, db=db)
        for key, value in kwargs.items():
            setattr(adv, key, value)
            await db.commit()
            await db.refresh(adv)
        return adv

    async def add_hashtag(self, adv_id: int, hashtag: str, db: AsyncSession) -> Advertisements:
        adv = await self.get_adv(adv_id=adv_id, db=db)
        if not adv.hashtags:
            adv.hashtags = hashtag
        else:
            adv.hashtags += " "
            adv.hashtags += hashtag
        await db.commit()
        await db.refresh(adv)
        return adv

    async def get_day_for_hash(self, adv_id: int, db: AsyncSession) -> str:
        adv = await self.get_adv(adv_id=adv_id, db=db)
        return adv.day_and_month


    async def current_adv_state(self, adv_id: int, bot: Bot, message: Message, db: AsyncSession, state: FSMContext) -> None:
        adv = await self.get_adv(adv_id=adv_id, db=db)
        if adv:
            theme = adv.theme if adv.theme is not None else ""
            name = adv.name if adv.name is not None else ""
            description = adv.description if adv.description is not None else ""
            date = adv.date if adv.date is not None else ""
            time = adv.time if adv.time is not None else ""
            members_count = adv.members_count if adv.members_count is not None else ""
            address = adv.address if adv.address is not None else ""
            price = adv.price if adv.price is not None else ""
            offer = adv.offer if (adv.offer is not None) and (adv.offer != "skip") else ""
            hashtags = adv.hashtags if adv.hashtags is not None else ""
            tg_owner_nick = adv.tg_name_owner if adv.tg_name_owner is not None else ""
            url_registration = adv.url_registration if adv.url_registration is not None else ""

            result = f"""
<strong> {theme} </strong>
«{name}» \n
{description} \n
🗓{date}
⏰{time}
👥Кол-во участников: {members_count}
🏢Место: {address}
💸Цена: {price} \n
{offer} \n
Разместил: @{tg_owner_nick} \n
{hashtags}  
"""
            if url_registration:
                registration_keyboard = url_keyboard(url_registration)
            else:
                registration_keyboard = None

            if len(result) > 1024:
                await message.answer(text="Объявление получилось слишком большим, максимальный размер - 1024 символа \n"
                                          "Начните ввод объявления сначала командой /start")
                await state.set_state(MainStates.start)
                raise ValueError

            await message.answer(text=f"Сейчас объявление выглядит так")
            if adv.photo == "skip":
                await message.answer(text=result, parse_mode="HTML", reply_markup=registration_keyboard)
            else:
                await bot.send_photo(chat_id=message.chat.id, photo=adv.photo, caption=result, parse_mode="HTML", reply_markup=registration_keyboard)


class SessionOrm():
    async def bind_user_session(self, user_chat_id: int, adv_id: int, db: AsyncSession) -> CurrentSessions:
        session_query = CurrentSessions(user_chat_id=user_chat_id, adv_id=adv_id)
        db.add(session_query)
        await db.commit()
        return session_query

    async def bind_exists(self, user_chat_id: int, adv_id: int, db: AsyncSession) -> bool:
        check_query = select(CurrentSessions).where(and_(CurrentSessions.user_chat_id == user_chat_id,
                                                         CurrentSessions.adv_id == adv_id))
        result = await db.execute(check_query)
        bind = result.scalars().first()
        return bool(bind)

    async def get_adv_id(self, chat_id: int, db: AsyncSession) -> Any:
        adv_query = select(CurrentSessions).where(CurrentSessions.user_chat_id == chat_id)
        result = await db.execute(adv_query)
        adv = result.scalars().first()
        if adv:
            return adv.adv_id
        else:
            return None

    async def bind_delete(self, user_chat_id: int, db: AsyncSession) -> bool:
        session_query = select(CurrentSessions).where(CurrentSessions.user_chat_id == user_chat_id)
        result = await db.execute(session_query)
        bind = result.scalars().first()
        if bind:
            await db.delete(bind)
            await db.commit()
            return True
        else:
            return False

user_orm = UserOrm()
adv_orm = AdvOrm()
session_orm = SessionOrm()