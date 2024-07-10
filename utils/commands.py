from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault
async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command="start",
            description="Старт создания объявления"
        ),
        BotCommand(
            command="cancel",
            description="Отмена создания объявления"
        )
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())