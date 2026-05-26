from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from typing import Callable, Awaitable, Dict, Any
import logging

from bot.core.keyboards import main_menu
from bot.services import AdminService
from bot.utils import show_screen

class ErrorHandlerMiddleware(BaseMiddleware):
  async def __call__(
    self,
    handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
    event: TelegramObject,
    data: Dict[str, Any]
  ) -> Any:
    try:
      return await handler(event, data)

    except Exception as e:
      logging.exception(f"💥 Глобальная ошибка: {e}")

      # Определяем куда отвечать
      message = None
      user = None

      if isinstance(event, Message):
        message = event
        user = event.from_user

      elif isinstance(event, CallbackQuery):
        message = event.message
        user = event.from_user

      if message:
        try:
          await message.answer(
            "❌ Произошла ошибка.\n\nВернитесь в меню и попробуйте снова.",
            reply_markup=main_menu(
                AdminService.is_admin(user.id, user.username)
            )
          )

        except Exception:
          pass

      return None