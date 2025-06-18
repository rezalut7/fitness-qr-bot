import os
from flask import Flask, request
import telebot

# ⚙️ Подгружаем токен из переменных окружения
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# 🌐 Flask-приложение
app = Flask(__name__)

# 📍 Главная страница (чтобы Render не ругался)
@app.route("/", methods=["GET"])
def index():
    return "Бот запущен!", 200

# 📩 Webhook-приёмник
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# 🟢 Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = telebot.types.KeyboardButton("✅ Согласен на обработку персональных данных и передачу тренеру DDX «Озерное»", request_contact=True)
    markup.add(button)
    bot.send_message(message.chat.id, "Привет! Пожалуйста, подтвердите согласие на обработку данных и отправьте свой номер телефона:", reply_markup=markup)

# 📞 Обработка номера телефона
@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    name = message.from_user.first_name or "Неизвестно"
    phone = message.contact.phone_number

    # 👁 Отправляем данные тебе или логируем
    bot.send_message(message.chat.id, f"Спасибо, {name}! Мы получили ваш номер: {phone}")
    
    # 🔒 Тут можно сохранить в базу, лог-файл, Google Sheet и т.д.
    print(f"[НОВЫЙ КЛИЕНТ] Имя: {name}, Телефон: {phone}")

# 🚀 Установка Webhook при запуске
if __name__ == "__main__":
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{BOT_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
