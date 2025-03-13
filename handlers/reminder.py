import re
from datetime import datetime, timedelta
from aiogram import types, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from apscheduler.schedulers.asyncio import AsyncIOScheduler

router = Router()
scheduler = AsyncIOScheduler()

class ReminderState(StatesGroup):
    waiting_for_time = State()

@router.message(Command("set_reminder"))
@router.message(F.text == "⏰ Напоминания")
async def set_reminder(message: types.Message, state: FSMContext):
    await message.answer("Введите время для напоминания в формате ЧЧ:ММ. Например, 08:00")
    await state.set_state(ReminderState.waiting_for_time)

@router.message(StateFilter(ReminderState.waiting_for_time))
async def handle_reminder_time(message: types.Message, state: FSMContext):
    time_pattern = r"^\d{2}:\d{2}$"
    if re.match(time_pattern, message.text):
        try:
            hour, minute = map(int, message.text.split(':'))
            now = datetime.now()
            reminder_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            if reminder_time < now:
                reminder_time += timedelta(days=1)

            from config import bot
            scheduler.add_job(send_reminder, 'date', run_date=reminder_time, args=[message.chat.id, message.text, bot])

            await message.answer(f"✅ Напоминание установлено на {message.text}!")
            await state.clear()
        except Exception as e:
            await message.answer(f"❌ Ошибка при обработке времени: {e}")
    else:
        await message.answer("❌ Ошибка! Убедитесь, что время введено в формате ЧЧ:ММ.")

async def send_reminder(chat_id, text, bot):
    await bot.send_message(chat_id, f"⏰ Напоминание: {text}")

async def run_scheduler():
    scheduler.start()