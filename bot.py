import telebot
from telebot import types
import requests
from datetime import datetime

# 🔑 Telegram Bot Token
BOT_TOKEN = '7968496888:AAHv52debk2DgW_mkfaW3S5FIkPOEVWof7A'
bot = telebot.TeleBot(BOT_TOKEN)

# 🔐 NocoDB Token
NOCO_TOKEN = 'kTJUuDfBwbq6E7ZWnqj6aFOyeJttdzhNWoBqhuwD'

# 🌐 NocoDB API URL
NOCO_URL = 'https://contacts-db.onrender.com/api/v1/db/data/v1/Getting Started/Контакты_Озерная'

# 👤 Обработка команды /start
@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = types.KeyboardButton("✅ Я подтверждаю согласие", request_contact=True)
    markup.add(button)

    bot.send_message(
        message.chat.id,
        "Нажимая на кнопку, вы подтверждаете согласие на обработку ваших персональных данных "
        "(ФИО и номер телефона) и передачу их тренеру фитнес-центра *DDX «Озерная»* "
        "в целях обратной связи и записи на тренировку.\n\n"
        "Никакие данные не передаются третьим лицам. "
        "Вы можете в любой момент отозвать согласие, написав нам в Telegram.",
        parse_mode="Markdown",
        reply_markup=markup
    )

# 📲 Обработка контакта
@bot.message_handler(content_types=['contact'])
def contact_handler(message):
    name = message.contact.first_name or "Без имени"
    phone = message.contact.phone_number
    now = datetime.now().isoformat()

    data = {
        "Имя": name,
        "НомерТелефона": phone,
        "Дата": now
    }

    headers = {
        "xc-token": NOCO_TOKEN,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(NOCO_URL, headers=headers, json=data)
        if response.status_code in [200, 201]:
            bot.send_message(message.chat.id, "✅ Контакт успешно сохранён!")
        else:
            bot.send_message(message.chat.id, f"❌ Ошибка сохранения: {response.status_code}\n{response.text}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка подключения: {str(e)}")

# 🔁 Запуск
bot.polling()
