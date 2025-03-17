from aiogram import types, Router, F
from aiogram.filters import Command
from database.db import delete_progress, get_progress

router = Router()


# Показ статистики с кнопками для удаления
@router.message(Command("stats"))
@router.message(F.text == "📊 Статистика")
async def show_stats(message: types.Message):
    user_id = message.from_user.id
    workouts = get_progress(user_id)
    if not workouts:
        await message.answer("❌ У вас нет сохранённых тренировок.")
        return

    response = "📊 *Ваша статистика по тренировкам:*\n\n"
    buttons = []

    for workout in workouts:
        workout_id, cat, exercise, reps, weight, date = workout
        response += f"ID: `{workout_id}`, Упражнение: {exercise}, Повторения: {reps}, Вес: {weight} кг, Дата: {date}\n"
        # Создаём inline-кнопку для удаления с callback_data
        buttons.append([
            types.InlineKeyboardButton(
                text=f"🗑 Удалить ID {workout_id}",
                callback_data=f"delete_{workout_id}"
            )
        ])

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer(response, parse_mode="Markdown", reply_markup=keyboard)


# Удаление через callback-кнопку
@router.callback_query(lambda c: c.data.startswith('delete_'))
async def delete_record_callback(callback_query: types.CallbackQuery):
    try:
        record_id = int(callback_query.data.split('_')[1])
        delete_progress(record_id)
        await callback_query.message.answer(f"✅ Запись с ID {record_id} удалена.")
        await callback_query.answer("Удалено ✅")
    except Exception as e:
        await callback_query.message.answer(f"❌ Ошибка при удалении: {e}")


# Удаление через текстовую команду
@router.message(Command("delete"))
async def delete_record(message: types.Message):
    try:
        args = message.text.split()
        if len(args) != 2:
            await message.answer("❌ Укажите ID записи для удаления. Пример: `/delete 1`")
            return

        record_id = int(args[1])
        delete_progress(record_id)
        await message.answer(f"✅ Запись с ID {record_id} удалена.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при удалении: {e}")
