from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from handlers import start, add, stats, history, reminder, delete, edit
from config import TOKEN
from handlers.reminder import run_scheduler


async def main():
    global dp
    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Подключаем все хэндлеры
    dp.include_router(start.router)
    dp.include_router(add.router)
    dp.include_router(stats.router)
    dp.include_router(history.router)
    dp.include_router(reminder.router)
    dp.include_router(delete.router)
    dp.include_router(edit.router)

    await run_scheduler()

    await bot.set_my_commands([
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/add", description="Добавить тренировку"),
        BotCommand(command="/stats", description="Показать статистику"),
        BotCommand(command="/history", description="Показать историю тренировок"),
        BotCommand(command="/set_reminder", description="Установить напоминание"),
        BotCommand(command="/delete", description="Удалить тренировку по ID"),
        BotCommand(command="/edit", description="Редактировать тренировку")
    ])

    print("✅ Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())