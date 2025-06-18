import asyncio, logging, os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from dotenv import load_dotenv
from database import Session, init_db
from models import Client
from datetime import datetime
from aiogram.fsm.state import StatesGroup, State

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

load_dotenv()
bot = Bot(os.getenv("BOT_TOKEN"), parse_mode="HTML")
dp = Dispatcher()

# --- Состояния ----------------------------------------------------
class Reg(StatesGroup):
    waiting_phone = State()
    waiting_consent = State()

# --- Хэндлеры -----------------------------------------------------
@dp.message(CommandStart())
async def start(m: Message, state):
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True,
        keyboard=[[KeyboardButton(text="Поделиться телефоном 📱", request_contact=True)]])
    await m.answer(
        "Привет! Я бот тренажёрного зала.\n"
        "🔒 Для записи поделитесь номером телефона.",
        reply_markup=kb)
    await state.set_state(Reg.waiting_phone)

@dp.message(Reg.waiting_phone, F.contact)
async def got_phone(m: Message, state):
    await state.update_data(phone=m.contact.phone_number)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("✅ Согласен", callback_data="consent_yes")],
        [InlineKeyboardButton("❌ Нет", callback_data="consent_no")],
    ])
    await m.answer(
        "Даю согласие на обработку персональных данных "
        "и их передачу тренеру (ФЗ-152)?",
        reply_markup=kb)
    await state.set_state(Reg.waiting_consent)

@dp.callback_query(Reg.waiting_consent, F.data.startswith("consent_"))
async def consent(cb, state):
    if cb.data == "consent_no":
        await cb.message.answer("Без согласия регистрация невозможна. До встречи!")
        await state.clear()
        return
    data = await state.get_data()
    async with Session() as s:
        s.add(Client(
            tg_id=cb.from_user.id,
            full_name=cb.from_user.full_name,
            phone=data["phone"],
            consent_at=datetime.utcnow(),
        ))
        await s.commit()
    btn = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton("Записаться на персональную тренировку",
                             callback_data="personal")
    ]])
    await cb.message.edit_text(
        "Отлично! Нажмите кнопку ниже, чтобы записаться.",
        reply_markup=btn)
    await state.clear()

@dp.callback_query(F.data == "personal")
async def personal(cb):
    await cb.message.edit_reply_markup()
    await cb.message.answer(
        "🎉 Спасибо! Тренер свяжется с вами в ближайшее время.")

# --- Запуск -------------------------------------------------------
async def main():
    await init_db()
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
