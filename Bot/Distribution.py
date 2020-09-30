import aiosqlite
import random
import time
import asyncio


async def pool_task(row):
    import Bot
    tg_id = row[0]
    await Bot.bot.send_message(chat_id=tg_id, text="Не забудь отметиться, когда придешь в ВУЦ. Хорошего дня!")


async def send_morning_messages(date):
    async with aiosqlite.connect("voenka_bot.db") as db:
        async with db.execute("SELECT tg_id FROM cold_attendance WHERE did_attend=1 and day=? and month=? and year=?",
                              [date.day, date.month, date.year]) as cursor:
            rows = await cursor.fetchall()
            await asyncio.gather(*[pool_task(row) for row in rows])
            await db.commit()

if __name__ == "__main__":
    pass
