import aiosqlite


async def add_to_db(user_id: int, fio: str, group_num: int):
    async with aiosqlite.connect("voenka_bot.db") as db:
        await db.execute("INSERT INTO users (fio, group_num, tg_id, is_active) VALUES (?, ?, ?, ?)", [fio, group_num, user_id, 1])
        await db.commit()


async def update_fio_group(user_id: int, fio: str, group_num: int):
    async with aiosqlite.connect("voenka_bot.db") as db:
        await db.execute("UPDATE users SET fio=?, group_num=? WHERE tg_id=?", [fio, group_num, user_id])
        await db.commit()


async def get_user_fio(user_id: int) -> str:
    async with aiosqlite.connect("voenka_bot.db") as db:
        async with db.execute("SELECT fio FROM users WHERE tg_id=?", [user_id]) as cursor:
            res = await cursor.fetchone()
            if res:
                return res[0]
            else:
                return None


async def get_user_group(user_id: int) -> str:
    async with aiosqlite.connect("voenka_bot.db") as db:
        async with db.execute("SELECT group_num FROM users WHERE tg_id=?", [user_id]) as cursor:
            res = await cursor.fetchone()
            if res:
                return res[0]
            else:
                return None


async def add_attendance(user_id: int, fio: str, group_num: int, date):
    async with aiosqlite.connect("voenka_bot.db") as db:
        await db.execute("INSERT INTO cold_attendance (fio, group_num, tg_id, day, month, year, did_attend) VALUES (?, ?, ?, ?, ?, ?, 1)",
                         [fio, group_num, user_id, date.day, date.month, date.year])
        await db.commit()


async def update_attendance(user_id: int, fio: str, group_num: int, date):
    async with aiosqlite.connect("voenka_bot.db") as db:
        await db.execute("UPDATE cold_attendance SET did_attend=1 WHERE tg_id=? and day=? and month=? and year=?",
                         [user_id, date.day, date.month, date.year])
        await db.commit()


async def is_in_attendance_db(user_id: int, date) -> bool:
    async with aiosqlite.connect("voenka_bot.db") as db:
        async with db.execute("SELECT tg_id FROM cold_attendance WHERE tg_id=? and day=? and month=? and year=?",
                              [user_id, date.day, date.month, date.year]) as cursor:
            res = await cursor.fetchone()
            if res:
                return True
            else:
                return False


async def did_attend_onday(user_id: int, date) -> bool:
    async with aiosqlite.connect("voenka_bot.db") as db:
        async with db.execute("SELECT did_attend FROM cold_attendance WHERE tg_id=? and day=? and month=? and year=?",
                              [user_id, date.day, date.month, date.year]) as cursor:
            res = await cursor.fetchone()
            if res:
                return res[0] == 1
            else:
                return None


async def get_attendance(user_id: int) -> list:
    async with aiosqlite.connect("voenka_bot.db") as db:
        async with db.execute("SELECT did_attend, day, month, year FROM cold_attendance WHERE tg_id=? ORDER BY year, month, day", [user_id]) as cursor:
            res = await cursor.fetchall()
            if res:
                return res
            else:
                return []


async def daily_attendance(group: int, date):
    async with aiosqlite.connect("voenka_bot.db") as db:
        await db.execute("INSERT INTO cold_attendance (fio, group_num, tg_id, day, month, year, did_attend) SELECT fio, group_num, tg_id, ?, ?, ?, 0 FROM users WHERE group_num / 100 = ?",
                         [date.day, date.month, date.year, group])
        await db.commit()


async def get_all_attendance() -> list:
    async with aiosqlite.connect("voenka_bot.db") as db:
        async with db.execute("SELECT did_attend, day, month, year, fio, group_num FROM cold_attendance ORDER BY fio, year, month, day") as cursor:
            res = await cursor.fetchall()
            if res:
                return res
            else:
                return []

if __name__ == "__main__":
    pass
