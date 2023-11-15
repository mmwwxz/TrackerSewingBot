import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor
from openpyxl import load_workbook
from datetime import datetime
from dotenv import load_dotenv
from handlers import markups as nav
from aiogram.dispatcher.filters.state import StatesGroup, State
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///mydatabase.db', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class Report(Base):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    name = Column(String)
    model_name = Column(String)
    remaining = Column(Integer)
    income = Column(Integer)
    expenses = Column(Integer)
    result1 = Column(Integer)


Base.metadata.create_all(engine)


Base = declarative_base()


logging.basicConfig(level=logging.INFO)

load_dotenv()
bot = Bot(os.getenv('TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
engine = create_engine('sqlite:///mydatabase.db', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


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


class FormSearch(StatesGroup):
    name_db = State()
    model_db = State()


# Определение модели для отчетов
# class Report(Base):
#     __tablename__ = 'reports'
#
#     id = Column(Integer, primary_key=True)
#     date = Column(DateTime(timezone=True), server_default=func.now())
#     name = Column(String)
#     model_name = Column(String)
#     remaining = Column(Integer)
#     income = Column(Integer)
#     expenses = Column(Integer)
#     result1 = Column(Integer)


# Определение модели для расходов
class Expenses(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    textile = Column(Integer)
    accessories = Column(Integer)
    sewing = Column(Integer)
    result2 = Column(Integer)


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

# --------- REPORTS ---------
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


# --------- SEARCH IN REPORTS FOR NAME ---------

@dp.message_handler(Text(equals="Поиск", ignore_case=True))
async def search_options(message: types.Message):
    print("Получено сообщение 'Поиск'")
    await message.reply("Выберите опцию поиска:", reply_markup=nav.filtrationMenu)


@dp.callback_query_handler(lambda c: c.data == "По имени")
async def search_by_name(callback_query: types.CallbackQuery):
    print("Получен запрос на поиск по имени")
    await bot.send_message(callback_query.from_user.id, "Введите имя мастера для поиска:")
    await FormSearch.name_db.set()

@dp.callback_query_handler(lambda c: c.data == "По названию модели")
async def search_by_model(callback_query: types.CallbackQuery):
    print("Получен запрос на поиск по названию модели")
    await bot.send_message(callback_query.from_user.id, "Введите название модели для поиска:")
    await FormSearch.model_db.set()

@dp.message_handler(state=FormSearch.name_db)
async def process_search_by_name(message: types.Message, state: FSMContext):
    print("Получено сообщение для поиска по имени:", message.text)
    async with state.proxy() as data:
        master_name = message.text

        results = session.query(Report).filter(Report.name == master_name).all()

        for result in results:
            await message.reply(f"Мастер: {result.name}, Модель: {result.model_name}, Количество: {result.remaining}, Принято: {result.income}")

    await state.finish()

# --------- SEARCH IN REPORTS FOR MODEL NAME ---------
@dp.message_handler(state=FormSearch.model_db)
async def process_search_by_model(message: types.Message, state: FSMContext):
    print("Получено сообщение для поиска по названию модели:", message.text)
    async with state.proxy() as data:
        model_name = message.text

        results = session.query(Report).filter(Report.model_name == model_name).all()

        for result in results:
            await message.reply(f"Мастер: {result.name}, Модель: {result.model_name}, Количество: {result.remaining}, Принято: {result.income}")

    await state.finish()


# --------- SEARCH IN EXPENSES ---------


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
async def process_reports(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['expenses'] = int(message.text)
        data['result1'] = str(int(data['income']) * int(data['expenses']))  # Итого = income * expenses

        new_report = Report(
            name=data['name'],
            model_name=data['model_name'],
            remaining=data['remaining'],
            income=data['income'],
            expenses=data['expenses'],
            result1=data['result1']
        )
        session.add(new_report)
        session.commit()

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

            new_expenses = Expenses(
                textile=data['textile'],
                accessories=data['accessories'],
                sewing=data['sewing'],
                result2=data['result2']
            )
            session.add(new_expenses)
            session.commit()

            with open(file_path, 'rb') as f:
                await bot.send_document(message.chat.id, f)
        except Exception as e:
            logging.error(f"Error sending document: {e}")
            print(f"Error sending document: {e}")

    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)