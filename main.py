import logging
import os
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor
from openpyxl import load_workbook
from datetime import datetime
from handlers import markups as nav
from config import class_for_main as nav2

if not os.path.exists('data'):
    os.makedirs('data', exist_ok=True)

if not os.path.exists('data/production.xlsx'):
    open('data/production.xlsx', 'w').close()

if not os.path.exists('data/consumption.xlsx'):
    open('data/consumption.xlsx', 'w').close()


@nav2.dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await message.reply("Привет! Я бот для учета производства. Нажмите кнопку \"Начать\", чтобы начать работу.",
                        reply_markup=nav.mainMenu)


# --------- REPORTS ---------

@nav2.dp.message_handler(Text(equals="Отчет", ignore_case=True))
async def process_name(message: types.Message):
    await message.reply("Введите ФИО мастера:")
    await nav2.FormReports.name.set()


@nav2.dp.message_handler(state=nav2.FormReports.name)
async def process_model_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.reply("Введите название модели:")
    await nav2.FormReports.model_name.set()


@nav2.dp.message_handler(state=nav2.FormReports.model_name)
async def process_model_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['model_name'] = message.text
    await message.reply("Введите количество изделий:")
    await nav2.FormReports.remaining.set()


@nav2.dp.message_handler(state=nav2.FormReports.remaining)
async def process_remaining(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['remaining'] = message.text
    await message.reply("Введите кол-во сколько приняли изделия:")
    await nav2.FormReports.income.set()


@nav2.dp.message_handler(state=nav2.FormReports.income)
async def process_unit_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['income'] = message.text
    await message.reply("Введите цену за единицу:")
    await nav2.FormReports.expenses.set()


# --------- SEARCH IN REPORTS BY NAME ---------

@nav2.dp.message_handler(Text(equals="Поиск", ignore_case=True))
async def search_options(message: types.Message):
    print("Получено сообщение 'Поиск'")
    await message.reply("Выберите опцию поиска:", reply_markup=nav.filtrationMenu)


@nav2.dp.callback_query_handler(lambda c: c.data == "По имени")
async def search_by_name(callback_query: types.CallbackQuery):
    print("Получен запрос на поиск по имени")
    await nav2.bot.send_message(callback_query.from_user.id, "Введите имя мастера для поиска:")
    current_state = await nav2.dp.storage.get_state(chat=callback_query.message.chat.id,
                                                    user=callback_query.from_user.id)
    print("Текущее состояние:", current_state)
    await nav2.FormSearch.name_db.set()


@nav2.dp.message_handler(state=nav2.FormSearch.name_db)
async def process_search_by_name(message: types.Message, state: FSMContext):
    print("Получено сообщение для поиска по имени:", message.text)
    async with state.proxy() as data:
        master_name = message.text

        results = nav2.session.query(nav2.Report).filter(nav2.Report.name == master_name).all()

        for result in results:
            await message.reply(f"Мастер: {result.name}, Модель: {result.model_name}, Количество: {result.remaining}"
                                f", Принято: {result.income}, Итог: {result.result1}")

    await state.finish()


# --------- SEARCH IN REPORTS BY MODEL NAME ---------

@nav2.dp.callback_query_handler(lambda c: c.data == "По названию модели")
async def search_by_model(callback_query: types.CallbackQuery):
    print("Получен запрос на поиск по названию модели")
    await nav2.bot.send_message(callback_query.from_user.id, "Введите название модели для поиска:")
    await nav2.FormSearch.model_db.set()


@nav2.dp.message_handler(state=nav2.FormSearch.model_db)
async def process_search_by_model(message: types.Message, state: FSMContext):
    print("Получено сообщение для поиска по названию модели:", message.text)
    async with state.proxy() as data:
        model_name = message.text

        results = nav2.session.query(nav2.Report).filter(nav2.Report.model_name == model_name).all()

        for result in results:
            await message.reply(f"Мастер: {result.name}, Модель: {result.model_name}, Количество: {result.remaining}"
                                f", Принято: {result.income}, Итог: {result.result1}")

    await state.finish()


# --------- EXPENSES ---------

@nav2.dp.message_handler(Text(equals="Расходы", ignore_case=True))
async def cmd_calc(message: types.Message):
    await message.reply("Введите расход за ткань:")
    await nav2.FormExpenses.textile.set()


@nav2.dp.message_handler(state=nav2.FormExpenses.textile)
async def expenses_by_accessories(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['textile'] = message.text
    await message.reply("Введите расходы за фурнитуру:")
    await nav2.FormExpenses.accessories.set()


@nav2.dp.message_handler(state=nav2.FormExpenses.accessories)
async def expenses_by_sewing(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['accessories'] = message.text
    await message.reply("Введите расходы на пошив за единицу:")
    await nav2.FormExpenses.sewing.set()


# --------- SEND REPORTS FILE ---------

@nav2.dp.message_handler(state=nav2.FormReports.expenses)
async def process_reports(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['expenses'] = int(message.text)
        data['result_reports'] = str(int(data['income']) * int(data['expenses']))  # Итого = income * expenses

        new_report = nav2.Report(
            name=data['name'],
            model_name=data['model_name'],
            remaining=data['remaining'],
            income=data['income'],
            expenses=data['expenses'],
            result_reports=data['result_reports']
        )
        nav2.session.add(new_report)
        nav2.session.commit()

        try:
            file_path_reports = 'data/production.xlsx'
            if os.path.exists(file_path_reports):
                wb = load_workbook(file_path_reports)
            else:
                wb = load_workbook(file_path_reports)
                ws = wb.active
                ws.append(["Дата", "Название модели", "Мастер ФИО", "Количество", "Принял", "Цена", "Итого"])

            ws = wb.active
            income = int(data['income'])
            remaining = int(data['remaining'])
            expenses = int(data['expenses'])
            result_reports = int(data['result_reports'])
            model_name = str(data['model_name'])
            name = str(data['name'])
            row = (datetime.now().strftime("%d.%m.%Y"), model_name, name, income, remaining, expenses, result_reports)
            ws.append(row)
            wb.save(file_path_reports)

            with open(file_path_reports, 'rb') as f:
                await nav2.bot.send_document(message.chat.id, f)
        except Exception as e:
            logging.error(f"Error sending document: {e}")
            print(f"Error sending document: {e}")

    await state.finish()


# --------- SEND EXPENSES FILE ---------

@nav2.dp.message_handler(state=nav2.FormExpenses.sewing)
async def process_expenses(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['sewing'] = message.text
        data['result_expenses'] = str(int(data['textile']) + int(data['accessories']) + int(data['sewing']))
        try:
            file_path_expenses = 'data/consumption.xlsx'
            if os.path.exists(file_path_expenses):
                wb = load_workbook(file_path_expenses)
            else:
                wb = load_workbook(file_path_expenses)
                ws = wb.active

            textile = int(data['textile'])
            accessories = int(data['accessories'])
            sewing = int(data['sewing'])
            result_expenses = int(data['result_expenses'])
            row = (datetime.now().strftime("%d.%m.%Y"), textile, accessories, sewing, result_expenses)
            ws.append(row)
            wb.save(file_path_expenses)

            new_expenses = nav2.Expenses(
                textile=data['textile'],
                accessories=data['accessories'],
                sewing=data['sewing'],
                result_expenses=data['result_expenses']
            )
            nav2.session.add(new_expenses)
            nav2.session.commit()

            with open(file_path_expenses, 'rb') as f:
                await nav2.bot.send_document(message.chat.id, f)
        except Exception as e:
            logging.error(f"Error sending document: {e}")
            print(f"Error sending document: {e}")

    await state.finish()


if __name__ == '__main__':
    executor.start_polling(nav2.dp, skip_updates=True)
