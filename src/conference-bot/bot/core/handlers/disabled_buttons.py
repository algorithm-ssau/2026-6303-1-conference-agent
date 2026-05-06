from aiogram import Router, F
from bot.core.constants import callbacks as cb
from aiogram.types import CallbackQuery 

router = Router()

@router.callback_query(F.data == cb.DISABLED)
async def disabled_handler(callback: CallbackQuery):
  """
    Обработчик для неактивных функций.

    - Показывает alert о том, что функция в разработке

    :param callback: CallbackQuery
  """
  await callback.answer(
    "🔧 Эта функция в разработке",
    show_alert=True
  )