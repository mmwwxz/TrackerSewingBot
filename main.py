import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from configparser import ConfigParser
from openpyxl import load_workbook
from datetime import datetime
from dotenv import load_dotenv
import sqlite3

from handlers import markups as nav

# import sqlite3
#
# conn = sqlite3.connect('data/reports.db')
# cursor = conn.cursor()
#
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS reports (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         date DATETIME NOT NULL DEFAULT (DATETIME('now')),
#         name STRING UNIQUE NOT NULL,
#         model_name STRING NOT NULL,
#         remaining INTEGER NOT NULL,
#         income INTEGER NOT NULL,
#         expenses INTEGER NOT NULL,
#         result1 INTEGER NOT NULL
#     )
# ''')
#
# conn.commit()

logging.basicConfig(level=logging.INFO)

load_dotenv()
bot = Bot(os.getenv('TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class FormReports(StatesGroup):
    name = State()
    model_name = State()
    remaining = State()
    income = State()
    expenses = State()
    result1 = State()


class FormExpenses(StatesGroup):
    textile = State()  # Ткань
    accessories = State()  # Фурнитура
    sewing = State()  # Пошив за ед.
    result2 = State()  # Итого


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await message.reply("Привет! Я бот для учета производства. Нажмите кнопку \"Начать\", чтобы начать работу.",
                        reply_markup=nav.mainMenu)


if not os.path.exists('data'):
    os.makedirs('data', exist_ok=True)

if not os.path.exists('data/production.xlsx'):
    open('data/production.xlsx', 'w').close()

if not os.path.exists('data/consumption.xlsx'):
    open('data/consumption.xlsx', 'w').close()


@dp.message_handler(Text(equals="Отчет", ignore_case=True))
async def process_name(message: types.Message):
    await message.reply("Введите ФИО мастера:")
    await FormReports.name.set()


@dp.message_handler(state=FormReports.name)
async def process_model_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.reply("Введите название модели:")
    await FormReports.model_name.set()


@dp.message_handler(state=FormReports.model_name)
async def process_model_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['model_name'] = message.text
    await message.reply("Введите количество изделий:")
    await FormReports.remaining.set()


@dp.message_handler(state=FormReports.remaining)
async def process_remaining(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['remaining'] = message.text
    await message.reply("Введите кол-во сколько приняли изделия:")
    await FormReports.income.set()


@dp.message_handler(state=FormReports.income)
async def process_unit_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['income'] = message.text
    await message.reply("Введите цену за единицу:")
    await FormReports.expenses.set()

# --- Расходы ---


@dp.message_handler(Text(equals="Расходы", ignore_case=True))
async def cmd_calc(message: types.Message):
    await message.reply("Введите расход за ткань:")
    await FormExpenses.textile.set()


@dp.message_handler(state=FormExpenses.textile)
async def expenses_for_accessories(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['textile'] = message.text
    await message.reply("Введите расходы за фурнитуру:")
    await FormExpenses.accessories.set()


@dp.message_handler(state=FormExpenses.accessories)
async def expenses_for_sewing(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['accessories'] = message.text
    await message.reply("Введите расходы на пошив за единицу:")
    await FormExpenses.sewing.set()


@dp.message_handler(state=FormReports.expenses)
async def process_result(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['expenses'] = int(message.text)
        data['result1'] = str(int(data['income']) * int(data['expenses']))  # Итого = income * expenses
        try:
            file_path = 'data/production.xlsx'
            if os.path.exists(file_path):
                wb = load_workbook(file_path)
            else:
                wb = load_workbook()
                ws = wb.active
                ws.append(["Дата", "Название модели", "Мастер ФИО", "Количество", "Принял", "Цена", "Итого"])

            ws = wb.active
            income = int(data['income'])
            remaining = int(data['remaining'])
            expenses = int(data['expenses'])
            result1 = int(data['result1'])
            model_name = str(data['model_name'])
            name = str(data['name'])
            row = (datetime.now().strftime("%d.%m.%Y"), model_name, name, income, remaining, expenses, result1)
            ws.append(row)
            wb.save(file_path)

            with open(file_path, 'rb') as f:
                await bot.send_document(message.chat.id, f)
        except Exception as e:
            logging.error(f"Error sending document: {e}")
            print(f"Error sending document: {e}")

    await state.finish()


@dp.message_handler(state=FormExpenses.sewing)
async def process_expenses(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['sewing'] = message.text
        data['result2'] = str(int(data['textile']) + int(data['accessories']) + int(data['sewing']))
        try:
            file_path = 'data/consumption.xlsx'
            if os.path.exists(file_path):
                wb = load_workbook(file_path)
            else:
                wb = load_workbook()
                ws = wb.active

            textile = int(data['textile'])
            accessories = int(data['accessories'])
            sewing = int(data['sewing'])
            result2 = int(data['result2'])
            row = (datetime.now().strftime("%d.%m.%Y"), textile, accessories, sewing, result2)
            ws.append(row)
            wb.save(file_path)

            with open(file_path, 'rb') as f:
                await bot.send_document(message.chat.id, f)
        except Exception as e:
            logging.error(f"Error sending document: {e}")
            print(f"Error sending document: {e}")

    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
