from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# --- Main menu ---
reports_btn = KeyboardButton('Отчет')
consumption_btn = KeyboardButton('Расходы')
filtration_btn = KeyboardButton('Фильтрация')

# --- Other menu ---
help_btn = KeyboardButton('Отправить баг')
mainMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(reports_btn, consumption_btn, filtration_btn,
                                                         help_btn)
