import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage


from bot.config import TOKEN
from bot.handlers import user, admin

async def main():
  bot = Bot(token=TOKEN)
  dp = Dispatcher(storage=MemoryStorage())

  dp.include_router(user.router)
  dp.include_router(admin.router)

  await dp.start_polling(bot)

if __name__ == "__main__":
  asyncio.run(main())