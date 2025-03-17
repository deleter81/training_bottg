from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import get_progress, update_progress
from handlers.history import show_history
from handlers.stats import show_stats

router = Router()

# Список доступных категорий
CATEGORIES = ["Грудь", "Спина", "Ноги", "Руки", "Плечи", "Кардио", "Общее"]

class EditWorkout(StatesGroup):
    waiting_for_id = State()
    waiting_for_new_category = State()
    waiting_for_new_values = State()

# Запуск редактирования тренировки
@router.message(Command("edit"))
@router.message(F.text == "✏️ Редактировать")
async def start_edit(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    workouts = get_progress(user_id)

    if not workouts:
        await message.answer("❌ У вас нет сохранённых тренировок.")
        return

    # Отображаем список тренировок с ID
    response = "📋 *Ваши тренировки:*\n\n"
    for workout in workouts:
        response += f"ID: `{workout[0]}` — {workout[2]} — {workout[3]} повторений, {workout[4]} кг, дата: {workout[5]}\n"

    response += "\nВведите ID тренировки, которую хотите изменить:"
    await message.answer(response, parse_mode="Markdown")
    await state.set_state(EditWorkout.waiting_for_id)

# Обрабатываем ввод ID
@router.message(EditWorkout.waiting_for_id)
async def process_id(message: types.Message, state: FSMContext):
    try:
        workout_id = int(message.text)
        await state.update_data(workout_id=workout_id)

        # Генерируем inline-кнопки для выбора категории
        buttons = [
            types.InlineKeyboardButton(text=category, callback_data=f"edit_category_{category}")
            for category in CATEGORIES
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons[i:i + 2] for i in range(0, len(buttons), 2)])

        await message.answer("Выберите новую категорию:", reply_markup=keyboard)
        await state.set_state(EditWorkout.waiting_for_new_category)

    except ValueError:
        await message.answer("❌ Неверный формат ID. Введите число.")

# Обрабатываем выбор новой категории
@router.callback_query(lambda c: c.data.startswith("edit_category_"))
async def process_new_category(callback_query: types.CallbackQuery, state: FSMContext):
    category = callback_query.data.split('_')[2]
    await state.update_data(category=category)

    await callback_query.message.answer(
        "Введите новые значения в формате:\n"
        "<b>Упражнение, количество повторений, вес, дата (гггг-мм-дд)</b>\n"
        "Например:\n<code>Приседания, 12, 60, 2025-03-22</code>",
        parse_mode="HTML"
    )

    await state.set_state(EditWorkout.waiting_for_new_values)

# Обрабатываем ввод новых значений
@router.message(EditWorkout.waiting_for_new_values)
async def process_new_values(message: types.Message, state: FSMContext):
    try:
        # Разделяем значения
        data = message.text.split(', ')
        if len(data) != 4:
            await message.answer(
                "❌ Неверный формат! Введите значения в формате: упражнение, повторения, вес, дата (гггг-мм-дд)")
            return

        # Сохраняем данные в переменные
        exercise, reps, weight, date = data[0], int(data[1]), float(data[2]), data[3]
        workout_data = await state.get_data()
        workout_id = workout_data["workout_id"]
        category = workout_data["category"]

        # Обновляем данные в базе
        update_progress(workout_id, category, exercise, reps, weight, date)

        # Подтверждение успешного обновления
        await message.answer(f"✅ Тренировка с ID `{workout_id}` успешно обновлена!\n📅 Дата: {date}")

        # Обновляем историю и статистику
        print("🔎 Обновляем историю...")
        await show_history(message, )
        print("🔎 Обновляем статистику...")
        await show_stats(message, state)
        print("✅ Оновлення завершено!")

        # Очищаем состояние FSM
        await state.clear()

    except ValueError:
        await message.answer("❌ Ошибка: Неверный формат числа. Убедитесь, что вы правильно ввели повторения и вес.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при обновлении тренировки: {e}")
