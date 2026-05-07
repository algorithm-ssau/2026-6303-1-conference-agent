import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramNetworkError, TelegramRetryAfter
from aiogram.client.default import DefaultBotProperties
from aiogram.client.telegram import TelegramAPIServer
from aiogram.client.session.aiohttp import AiohttpSession
from bot.config import TOKEN, PROXY_URL, GROQ_API_KEY
from bot.core.handlers import callbacks_router, get_admin_router, user_router, disabled_handler
from bot.database.schema import init_db

logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logging.getLogger("aiohttp").setLevel(logging.WARNING)

async def on_startup():
  init_db()
  logging.info("Бот запущен!")


async def on_shutdown():
  logging.info("Бот остановлен!")


async def main():
  timeout = 60
  custom_server = TelegramAPIServer.from_base(PROXY_URL)
  session = AiohttpSession(api=custom_server, timeout=timeout)
  
  bot = Bot(
    token=TOKEN, 
    session=session,
    default=DefaultBotProperties(parse_mode="HTML")
  )
  
  dp = Dispatcher(storage=MemoryStorage())
  
  dp.startup.register(on_startup)
  dp.shutdown.register(on_shutdown)
  
  dp.include_router(disabled_handler)
  dp.include_router(callbacks_router)  # общие
  dp.include_router(user_router)     # пользовательские
  dp.include_router(get_admin_router()) # админские
  
  while True:
    try:
      await dp.start_polling(bot)
    except TelegramNetworkError as e:
      logging.error(f"Ошибка сети: {e}. Переподключение через 5 секунд...")
      await asyncio.sleep(5)
    except TelegramRetryAfter as e:
      logging.error(f"Слишком много запросов. Повтор через {e.retry_after} секунд")
      await asyncio.sleep(e.retry_after)
    except Exception as e:
      logging.error(f"Неожиданная ошибка: {e}")
      await asyncio.sleep(3)


if __name__ == "__main__":
  try:
    asyncio.run(main())
  except KeyboardInterrupt:
    logging.info("Бот остановлен пользователем")