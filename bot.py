import os
import csv
from datetime import datetime
from flask import Flask, request
import telebot

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

CSV_FILE = "clients.csv"

# Создание файла с заголовками, если его нет
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Имя", "Телефон", "Дата"])

@app.route("/", methods=["GET"])
def index():
    return "Бот работает и сохраняет в CSV", 200

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    args = message.text.split()
    if len(args) > 1 and args[1] == "consent":
        show_consent_message(message)
    else:
        bot.send_message(message.chat.id, "Привет! Для начала отсканируйте QR-код.")

def show_consent_message(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = telebot.types.KeyboardButton("✅ Согласен и отправляю телефон", request_contact=True)
    markup.add(button)

    text = (
        "🔒 *Согласие на обработку персональных данных*\n\n"
        "Нажимая на кнопку, вы подтверждаете согласие на обработку ваших персональных данных "
        "(ФИО и номер телефона) и передачу их тренеру фитнес-центра *DDX «Озерная»* "
        "в целях обратной связи и записи на тренировку.\n\n"
        "Никакие данные не передаются третьим лицам. "
        "Вы можете в любой момент отозвать согласие, написав нам в Telegram."
    )

    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    name = message.from_user.first_name or "Неизвестно"
    phone = message.contact.phone_number
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([name, phone, now])

    bot.send_message(message.chat.id, f"Спасибо, {name}! Мы записали ваш номер: {phone}")

if __name__ == "__main__":
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{BOT_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
