import re
from datetime import datetime
from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from database.db import add_progress

router = Router()

# Список доступных категорий и упражнений
CATEGORIES = ["Грудь", "Спина", "Ноги", "Руки", "Плечи", "Кардио", "Общее"]
EXERCISES = {
    "Грудь": ["Жим лёжа", "Отжимания", "Разводка"],
    "Спина": ["Тяга штанги", "Подтягивания", "Тяга блока"],
    "Ноги": ["Приседания", "Выпады", "Жим ногами"],
    "Руки": ["Сгибания на бицепс", "Французский жим", "Молотки"],
    "Плечи": ["Жим гантелей", "Махи в стороны", "Подъём перед собой"],
    "Кардио": ["Бег", "Велосипед", "Прыжки на скакалке"],
    "Общее": ["Планка", "Берпи", "Подтягивания"]
}

# FSM для последовательного ввода данных
class AddWorkout(StatesGroup):
    waiting_for_category = State()
    waiting_for_exercise = State()
    waiting_for_weight = State()
    waiting_for_reps = State()
    waiting_for_date = State()

# Старт добавления тренировки (выбор категории)
@router.message(Command("add"))
@router.message(F.text == "➕ Добавить")
async def start_add(message: types.Message, state: FSMContext):
    await state.clear()

    # Создание кнопок для категорий
    buttons = [
        types.InlineKeyboardButton(text=category, callback_data=f"category_{category}")
        for category in CATEGORIES
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons[i:i + 2] for i in range(0, len(buttons), 2)])

    await message.answer("Выберите категорию тренировки:", reply_markup=keyboard)
    await state.set_state(AddWorkout.waiting_for_category)

# Обрабатываем выбор категории → Показ упражнений
@router.callback_query(lambda c: c.data.startswith('category_'))
async def process_category(callback_query: types.CallbackQuery, state: FSMContext):
    category = callback_query.data.split('_')[1]
    await state.update_data(category=category)

    exercises = EXERCISES.get(category, [])
    buttons = [
        types.InlineKeyboardButton(text=exercise, callback_data=f"exercise_{exercise}")
        for exercise in exercises
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons[i:i + 2] for i in range(0, len(buttons), 2)])

    await callback_query.message.edit_text(
        f"✅ Категория выбрана: *{category}*\nТеперь выберите упражнение:",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await state.set_state(AddWorkout.waiting_for_exercise)

# Обрабатываем выбор упражнения → Ввод веса
@router.callback_query(lambda c: c.data.startswith('exercise_'))
async def process_exercise(callback_query: types.CallbackQuery, state: FSMContext):
    exercise = callback_query.data.split('_')[1]
    await state.update_data(exercise=exercise)

    await callback_query.message.edit_text(
        f"✅ Упражнение выбрано: *{exercise}*\nВведите вес (в кг):",
        parse_mode="Markdown"
    )
    await state.set_state(AddWorkout.waiting_for_weight)

# Ввод веса → Ввод повторений
@router.message(AddWorkout.waiting_for_weight)
async def process_weight(message: types.Message, state: FSMContext):
    try:
        weight = float(message.text)
        await state.update_data(weight=weight)

        await message.answer("Введите количество повторений:")
        await state.set_state(AddWorkout.waiting_for_reps)

    except ValueError:
        await message.answer("❌ Введите корректное значение веса (например, 75.5).")

# Ввод повторений → Ввод даты
@router.message(AddWorkout.waiting_for_reps)
async def process_reps(message: types.Message, state: FSMContext):
    try:
        reps = int(message.text)
        await state.update_data(reps=reps)

        await message.answer("Введите дату тренировки (в формате ДД.ММ.ГГГГ):")
        await state.set_state(AddWorkout.waiting_for_date)

    except ValueError:
        await message.answer("❌ Введите корректное значение повторений (например, 10).")

# Ввод даты → Сохранение данных в базу
@router.message(AddWorkout.waiting_for_date)
async def process_date(message: types.Message, state: FSMContext):
    try:
        # Проверяем формат даты
        date_pattern = r"^\d{2}\.\d{2}\.\d{4}$"
        if not re.match(date_pattern, message.text):
            raise ValueError("Неверный формат даты! Используйте формат: дд.мм.гггг")

        date = datetime.strptime(message.text, "%d.%m.%Y").strftime("%Y-%m-%d")

        # Получаем данные из state
        data = await state.get_data()
        category = data["category"]
        exercise = data["exercise"]
        weight = data["weight"]
        reps = data["reps"]

        # Сохраняем в базу данных
        add_progress(
            user_id=message.from_user.id,
            exercise=exercise,
            category=category,
            reps=reps,
            weight=weight,
            date=date
        )

        await message.answer(
            f"✅ Данные успешно сохранены:\n"
            f"🏋️‍♂️ Упражнение: *{exercise}*\n"
            f"📅 Дата: *{date}*\n"
            f"⚖️ Вес: *{weight} кг*\n"
            f"🔁 Повторений: *{reps}*\n",
            parse_mode="Markdown"
        )
        await state.clear()

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
