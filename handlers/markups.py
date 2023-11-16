from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import types

# --- Main menu ---
reports_btn = KeyboardButton('Отчет')
consumption_btn = KeyboardButton('Расходы')
filtration_btn = KeyboardButton('Поиск')

# --- Filtration menu ---
name_filtration_btn = KeyboardButton('По имени')
model_name_filtration_btn = KeyboardButton('По названию модели')

# --- Other menu ---
help_btn = KeyboardButton('Отправить баг')
mainMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(reports_btn, consumption_btn, filtration_btn, help_btn)

filtrationMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(name_filtration_btn, model_name_filtration_btn)

