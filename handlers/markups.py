from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

# --- MAIN MENU ---
reports_btn = KeyboardButton('Отчет')
consumption_btn = KeyboardButton('Расходы')
filtration_btn = KeyboardButton('Поиск')

# --- FILTRATION MENU ---
name_filtration_btn = KeyboardButton('По имени')
model_name_filtration_btn = KeyboardButton('По названию модели')

# --- OTHER MENU ---
help_btn = KeyboardButton('Отправить баг')
mainMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(reports_btn, consumption_btn, filtration_btn, help_btn)

filtrationMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(name_filtration_btn, model_name_filtration_btn)

# --- INLINE MENU ---
import_file = InlineKeyboardButton('Отправить exel файл')

file = InlineKeyboardMarkup(resize_keyboard=True).add(import_file)
