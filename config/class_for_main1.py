from aiogram.dispatcher.filters.state import StatesGroup, State
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
import logging
import os
from aiogram import Dispatcher, Bot

engine = create_engine('sqlite:///mydatabase.db', echo=True)
Base = declarative_base()

# ---- BOT TOKEN ----
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
    result_reports = State()


class FormExpenses(StatesGroup):
    textile = State()
    accessories = State()
    sewing = State()
    result_expenses = State()


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
    result_reports = Column(Integer)


class Expenses(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    textile = Column(Integer)
    accessories = Column(Integer)
    sewing = Column(Integer)
    result_expenses = Column(Integer)


# Создаем таблицы в нужном порядке
Base.metadata.create_all(engine, tables=[Report.__table__])
Base.metadata.create_all(engine, tables=[Expenses.__table__])

Session = sessionmaker(bind=engine)
session = Session()
