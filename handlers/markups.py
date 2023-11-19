from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# --- MAIN MENU ---
reports_btn = KeyboardButton('Отчет 📊')
consumption_btn = KeyboardButton('Расходы 💸')
filtration_btn = KeyboardButton('Поиск 🔍')
help_btn = KeyboardButton('Отправить баг 🐛')
support_btn = KeyboardButton('Техподдержка 🛠')

mainMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(reports_btn, consumption_btn, filtration_btn, help_btn,
                                                         support_btn)


# --- OTHER MENU ---


# --- INLINE MENU ---
# import_file = InlineKeyboardButton('Отправить exel файл')
#
# file = InlineKeyboardMarkup(resize_keyboard=True).add(import_file)
