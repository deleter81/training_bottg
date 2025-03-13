from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database.db import get_progress, delete_progress
import io
import matplotlib.pyplot as plt

router = Router()


# ✅ Генерация графика по всем данным
def generate_graph(user_id):
    workouts = get_progress(user_id)
    if not workouts:
        return None

    exercises = []
    weights = []
    reps = []
    dates = []

    for workout in workouts:
        workout_id, cat, exercise, reps_count, weight, date = workout
        exercises.append(exercise)
        weights.append(weight)
        reps.append(reps_count)
        dates.append(date)

    if not dates:
        return None

    plt.figure(figsize=(10, 6))
    plt.plot(dates, weights, marker='o', label='Вес', color='blue')
    plt.plot(dates, reps, marker='s', label='Повторения', color='red')
    plt.title('Прогресс по тренировкам')
    plt.xlabel('Дата')
    plt.ylabel('Вес / Повторения')
    plt.legend()
    plt.grid(True)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    return buffer


# ✅ Показ статистики и графика с кнопками удаления
async def show_stats_by_category(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await state.clear()

    workouts = get_progress(user_id)
    if not workouts:
        await message.answer("❌ У вас нет сохранённых тренировок.")
        return

    response = "📊 *Ваша статистика по тренировкам:*\n\n"
    buttons = []

    for workout in workouts:
        workout_id, cat, exercise, reps, weight, date = workout
        response += f"ID: `{workout_id}`, Упражнение: {exercise}, Повторения: {reps}, Вес: {weight} кг, Дата: {date}\n"

        # ✅ Добавляем инлайн-кнопку для удаления записи
        buttons.append([
            types.InlineKeyboardButton(
                text=f"🗑 Удалить ID {workout_id}",
                callback_data=f"delete_{workout_id}"
            )
        ])

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    # ✅ Отправляем сообщение с кнопками
    await message.answer(response, parse_mode="Markdown", reply_markup=keyboard)

    # ✅ Генерация графика
    graph = generate_graph(user_id)
    if graph:
        await message.answer_photo(types.BufferedInputFile(graph.getvalue(), filename="stats.png"))
    else:
        await message.answer("📊 Недостаточно данных для построения графика.")


# ✅ Обработка удаления через инлайн-кнопку
@router.callback_query(lambda c: c.data.startswith('delete_'))
async def delete_record_callback(callback_query: types.CallbackQuery):
    try:
        record_id = int(callback_query.data.split('_')[1])

        # ✅ Удаляем запись из базы данных
        delete_progress(record_id)

        # ✅ Удаляем кнопку и обновляем текст сообщения
        updated_text = callback_query.message.text.replace(
            f"🗑 Удалить ID {record_id}\n", ""
        )

        if updated_text.strip() == "📊 *Ваша статистика по тренировкам:*":
            updated_text = "📊 У вас нет сохранённых тренировок."

        await callback_query.message.edit_text(updated_text, parse_mode="Markdown")

        # ✅ Показываем уведомление о том, что запись удалена
        await callback_query.answer("✅ Запись удалена.")

    except Exception as e:
        await callback_query.message.answer(f"❌ Ошибка при удалении: {e}")


# ✅ Команда /stats
@router.message(Command("stats"))
@router.message(F.text == "📊 Статистика")
async def show_stats(message: types.Message, state: FSMContext):
    await state.clear()
    await show_stats_by_category(message, state)