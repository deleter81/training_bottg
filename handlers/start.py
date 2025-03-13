from aiogram import types, Router
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="➕ Добавить"), types.KeyboardButton(text="📊 Статистика"), types.KeyboardButton(text="📖 История")],
            [types.KeyboardButton(text="⏰ Напоминания"), types.KeyboardButton(text="✏️ Редактировать"),]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "Привет! Я бот для отслеживания прогресса в тренировках. Вы можете:\n"
        "- Добавить результаты (/add)\n"
        "- Посмотреть статистику (/stats)\n"
        "- Историю тренировок (/history)\n"
        "- Установить напоминания (/set_reminder)\n"
        "- Редактировать результаты (/edit)\n"
        "- Удалить результаты (/delete)\n",
        reply_markup=keyboard
    )