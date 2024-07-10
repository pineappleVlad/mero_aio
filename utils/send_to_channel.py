from aiogram import Bot
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Advertisements
from keyboards.inline import url_keyboard


async def send_to_channel(adv: Advertisements, id_channel: int, channel_type: str, bot: Bot):
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

    result_long = f"""
<strong>{theme}</strong>
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

    result_short = f"""
<strong>{theme}</strong>
«{name}» \n
🗓{date}
⏰{time}
👥Кол-во участников: {members_count}
{offer} \n
{hashtags}    
    """

    if channel_type == "long":
        if adv.photo == "skip":
            await bot.send_message(chat_id=id_channel, text=result_long, parse_mode="HTML",
                                   reply_markup=url_keyboard(url_registration))
        else:
            await bot.send_photo(chat_id=id_channel, photo=adv.photo, caption=result_long, parse_mode="HTML",
                                 reply_markup=url_keyboard(url_registration))
    elif channel_type == "short":
        if adv.photo == "skip":
            await bot.send_message(chat_id=id_channel, text=result_short, parse_mode="HTML",
                                   reply_markup=url_keyboard(url_registration))
        else:
            await bot.send_photo(chat_id=id_channel, photo=adv.photo, caption=result_short, parse_mode="HTML",
                                 reply_markup=url_keyboard(url_registration))