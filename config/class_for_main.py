import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
from aiogram.dispatcher.filters.state import StatesGroup, State
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)
load_dotenv()
bot = Bot(os.getenv('TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
engine = create_engine('sqlite:///mydatabase.db', echo=True)
Base = declarative_base()
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


class FormReports(StatesGroup):
    name = State()
    model_name = State()
    remaining = State()
    income = State()
    expenses = State()
    result_reports = State()


class FormExpenses(StatesGroup):
    textile = State()  # Ткань
    accessories = State()  # Фурнитура
    sewing = State()  # Пошив за ед.
    result_expenses = State()  # Итого


class FormSearch(StatesGroup):
    name_db = State()
    model_db = State()


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


# Определение модели для расходов
class Expenses(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    textile = Column(Integer)
    accessories = Column(Integer)
    sewing = Column(Integer)
    result2 = Column(Integer)