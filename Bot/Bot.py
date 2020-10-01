import logging
import aiosqlite
import re
import random
import time
import datetime
import asyncio
import pytz
import aiogram.utils.markdown as md

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import Database
import Report
from Distribution import send_morning_messages

API_TOKEN = '1177540873:AAFinUzdAa5asNNb6Qu1DLhzPw-Uv31B4J4'  # TODO: change token

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    fio_registration = State()
    group_registration = State()


# TODO: call this at 8:46 AM
async def create_report():
    curr_day = datetime.datetime.today().weekday()
    if curr_day < 2 or curr_day > 4:  # not voenka days
        return
    await Report.create_report()


# TODO: call this every day at 7 AM
async def daily_attendance():
    curr_day = datetime.datetime.today().weekday()
    if curr_day < 2 or curr_day > 4:  # not voenka days
        return
    groups_by_day = {2: 19, 3: 20, 4: 18}
    await Database.daily_attendance(group=groups_by_day[curr_day], date=datetime.datetime.now())
    await send_morning_messages(date=datetime.datetime.now())


async def is_time_correct(group: int):
    tz = pytz.timezone('Europe/Moscow')  # getting current Moscow time
    msk_now = datetime.datetime.now(tz)
    min_time = 7 * 60  # 7 AM
    max_time = 8 * 60 + 46  # 8:46 AM
    curr_time = msk_now.hour * 60 + msk_now.minute
    if curr_time < min_time or curr_time >= max_time:
        return False

    group //= 100
    # mon==0, wed==2 and etc
    curr_day = datetime.datetime.today().weekday()
    # Update this every year? since group numbers change
    return group == 19 and curr_day == 2 or group == 20 and curr_day == 3 or group == 18 and curr_day == 4


@dp.message_handler(Text(equals='Отметить присутствие', ignore_case=True))
async def attend(message: types.Message):
    try:
        user_id = message.chat.id
    except:
        await message.answer("Error with user_id")
        return

    fio = await Database.get_user_fio(user_id=user_id)
    group = await Database.get_user_group(user_id=user_id)
    if group:
        if await is_time_correct(group):
            if await Database.did_attend_onday(user_id, datetime.datetime.now()):
                await message.answer("Ты сегодня уже отметился.")
            else:
                await Database.add_attendance(user_id, fio, group, datetime.datetime.now())
                await message.answer("Молодец, ты отметился.")
        else:
            await message.answer("Отметиться можно только в свой военный день с 7:00 до 8:45")
    else:
        await message.answer("Ошибка в номере взвода.")
        return


@dp.message_handler(Text(equals='Мои посещения', ignore_case=True))
async def check_attendance(message: types.Message):
    try:
        user_id = message.chat.id
    except:
        await message.answer("Error with user_id")
        return

    att_list = await Database.get_attendance(user_id)

    str_to_send = ''
    for elem in att_list:
        if elem[0]:
            str_to_send += "{:02}.{:02}.{:02} ✅\n".format(elem[1], elem[2], elem[3])
        else:
            str_to_send += "{:02}.{:02}.{:02} ❌\n".format(elem[1], elem[2], elem[3])

    if str_to_send == '':
        str_to_send = 'У тебя еще нет данных о посещениях'

    await message.answer(text=str_to_send)


@dp.message_handler(Text(equals='Отмена', ignore_case=True), state=Form.fio_registration)
async def cancel_git(message: types.Message, state: FSMContext):
    try:
        user_id = message.chat.id
    except:
        await message.answer("Error with user_id")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Отметить присутствие")
    markup.add("Мои посещения", "Мои данные")
    markup.add("Изменить данные", "Обратная связь")

    await message.answer("Изменение данных отменено.", reply_markup=markup)
    await state.finish()


@dp.message_handler(Text(equals='Изменить данные', ignore_case=True))
async def change_data(message: types.Message):
    try:
        user_id = message.chat.id
    except:
        await message.answer("Error with user_id")
        return

    await Form.fio_registration.set()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Отмена")
    await message.answer("Введи своё ФИО через пробел.", reply_markup=markup)


@dp.message_handler(Text(equals='Мои данные', ignore_case=True))
async def get_data(message: types.Message):
    try:
        user_id = message.chat.id
    except:
        await message.answer("Error with user_id")
        return

    fio = await Database.get_user_fio(user_id=user_id)
    group = await Database.get_user_group(user_id=user_id)

    if fio:
        await message.answer(f'ФИО: {fio}')
    else:
        await message.answer('Ошибка в ФИО')

    if group:
        await message.answer(f'Взвод: {group}')
    else:
        await message.answer('Ошибка в номере взвода')


@dp.message_handler(Text(equals='Обратная связь', ignore_case=True))
async def contact(message: types.Message):
    await message.answer("Для обратной связи пиши: @th3luck")


@dp.message_handler(state=Form.group_registration)
async def process_group(message: types.Message, state: FSMContext):
    try:
        user_id = message.chat.id
    except:
        await message.answer("Error with user_id")
        return

    try:
        # TODO: check if group really exists
        group_num = int(message.text)
        async with state.proxy() as data:
            data['group_num'] = group_num
    except:
        await message.answer("Неверный номер взвода")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Отметить присутствие")
    markup.add("Мои посещения", "Мои данные")
    markup.add("Изменить данные", "Обратная связь")

    if await Database.get_user_fio(user_id=user_id):
        # old user
        await Database.update_fio_group(user_id, data['fio'], data['group_num'])
        await message.answer("Данные обновлены.", reply_markup=markup)
    else:
        # new user
        await Database.add_to_db(user_id, data['fio'], data['group_num'])
        await message.answer("Ты успешно зарегистрировался.", reply_markup=markup)

    await state.finish()


@dp.message_handler(Text, state=Form.fio_registration)
async def process_fio(message: types.Message, state: FSMContext):
    try:
        user_id = message.chat.id
    except:
        await message.answer("Error with user_id")
        return

    async with state.proxy() as data:
        data['fio'] = message.text
    await message.answer("Введи свой номер взвода. Например: 1911")
    await Form.next()


@dp.message_handler(commands='start', state='*')
async def cmd_start(message: types.Message):
    await create_report()
    await message.answer("Здравия желаю, товарищ!")
    try:
        user_id = message.chat.id
    except:
        await message.answer("Error with user_id")
        return

    # checking if user already exists
    if await Database.get_user_fio(user_id=user_id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("Отметить присутствие")
        markup.add("Мои посещения", "Мои данные")
        markup.add("Изменить данные", "Обратная связь")
        await message.answer("Ты уже зарегистрирован.", reply_markup=markup)
        return

    await Form.fio_registration.set()
    await message.answer("Введи своё ФИО через пробел.", reply_markup=types.ReplyKeyboardRemove())


if __name__ == '__main__':
    # Run pipeline once a day
    scheduler = AsyncIOScheduler()
    scheduler.add_job(daily_attendance, 'cron', hour=7, minute=0,
                      second=0, timezone="Europe/Moscow")  # msk 7 AM
    scheduler.add_job(create_report, 'cron', hour=8, minute=50, second=0,
                      timezone="Europe/Moscow")  # msk 8:50 AM
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)
