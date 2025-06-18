import asyncio, logging, os
from datetime import datetime
from functools import partial

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message, CallbackQuery,
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv

from database_ydb import save_client

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

load_dotenv()
bot = Bot(os.getenv("BOT_TOKEN"), parse_mode="HTML")
dp = Dispatcher()

class Reg(StatesGroup):
    waiting_consent = State()
    waiting_phone   = State()

@dp.message(CommandStart())
async def start(m: Message, state):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("✅ Согласен", callback_data="yes")],
        [InlineKeyboardButton("❌ Не согласен", callback_data="no")],
    ])
    await m.answer(
        "Привет! Я бот тренажёрного зала.\n\n"
        "Даю согласие на обработку персональных данных (ФЗ-152)?",
        reply_markup=kb,
    )
    await state.set_state(Reg.waiting_consent)

@dp.callback_query(Reg.waiting_consent, F.data.in_(["yes", "no"]))
async def consent(cb: CallbackQuery, state):
    if cb.data == "no":
        await cb.message.answer("Окей, без согласия никак. /start — если передумаешь.")
        await state.clear()
        return

    await state.update_data(consent_at=datetime.utcnow())
    kb = ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True,
        keyboard=[[KeyboardButton("Отправить телефон 📱", request_contact=True)]],
    )
    await cb.message.edit_text("Спасибо! Теперь отправь номер телефона:")
    await cb.message.answer("⬇️ Жми кнопку ниже", reply_markup=kb)
    await state.set_state(Reg.waiting_phone)

@dp.message(Reg.waiting_phone, F.contact)
async def phone(msg: Message, state):
    data = await state.get_data()
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None,
        partial(
            save_client,
            msg.from_user.id,
            msg.from_user.full_name,
            msg.contact.phone_number,
            data["consent_at"],
        ),
    )

    btn = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton("Записаться на персональную тренировку", callback_data="personal")
    ]])
    await msg.answer("Отлично! Жми кнопку, чтобы записаться 👇", reply_markup=btn)
    await state.clear()

@dp.callback_query(F.data == "personal")
async def personal(cb: CallbackQuery):
    await cb.message.edit_reply_markup()
    await cb.message.answer("🎉 Вы записаны! Тренер скоро свяжется. Спасибо!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
