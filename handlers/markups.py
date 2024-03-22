from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# --- MAIN MENU ---
reports_btn = KeyboardButton('Отчет 📊')
consumption_btn = KeyboardButton('Расходы 💸')
filtration_btn = KeyboardButton('Поиск 🔍')

mainMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(reports_btn, consumption_btn, filtration_btn)
