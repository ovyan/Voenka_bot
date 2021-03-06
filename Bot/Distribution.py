import aiosqlite
import random
import time
import asyncio
from aiogram import types


async def pool_task(row):
    import Bot
    tg_id = row[0]
    try:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("Отметить присутствие")
        markup.add("Мои посещения", "Мои данные")
        markup.add("Изменить данные", "Обратная связь")
        await Bot.bot.send_message(chat_id=tg_id, text="Не забудь отметиться, когда придешь в ВУЦ. Хорошего дня!", reply_markup=markup)
    except:
        pass


async def send_morning_messages(date):
    async with aiosqlite.connect("voenka_bot.db") as db:
        async with db.execute("SELECT tg_id FROM cold_attendance WHERE did_attend=0 and day=? and month=? and year=?",
                              [date.day, date.month, date.year]) as cursor:
            rows = await cursor.fetchall()
            await asyncio.gather(*[pool_task(row) for row in rows])
            await db.commit()

if __name__ == "__main__":
    pass
