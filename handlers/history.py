from aiogram import Router, types, F
from aiogram.filters import Command
from database.db import get_progress
router = Router()


@router.message(Command("history"))
@router.message(F.text == "📖 История")
async def show_history(message: types.Message):
    user_id = message.from_user.id
    workouts = get_progress(user_id)  # Всегда берём актуальные данные

    if not workouts:
        await message.answer("❌ У вас нет сохранённых тренировок.")
        return

    response = "📖 *Ваша история тренировок:*\n\n"
    for workout in workouts:
        exercise, reps, weight, date = workout[2:]
        response += f"🏆 {exercise} — {reps} повторений, {weight} кг, дата: {date}\n"

    await message.answer(response, parse_mode="Markdown")
