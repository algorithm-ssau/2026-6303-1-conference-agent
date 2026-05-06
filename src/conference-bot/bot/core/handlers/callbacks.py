from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.core.constants import callbacks as cb, MESSAGES
from bot.core.keyboards import main_menu, back_button
from bot.config import ADMIN_IDS


router = Router()

@router.callback_query(F.data == cb.MAIN_MENU)
async def main_menu_handler(callback: CallbackQuery, state: FSMContext):
  """
    Возвращает пользователя в главное меню.

    - Очищает FSM
    - Определяет, является ли пользователь администратором
    - Показывает соответствующее меню

    :param callback: CallbackQuery
    :param state: FSMContext
  """
  await state.clear()
  is_admin = callback.from_user.id in ADMIN_IDS

  await callback.message.edit_text(
    MESSAGES["callbacks"]["main-menu"], 
    reply_markup=main_menu(is_admin)
  )
  
@router.callback_query(F.data == cb.ABOUT)
async def about_handler(callback: CallbackQuery):
  """
    Показывает информацию о боте.

    :param callback: CallbackQuery
  """
  await callback.message.edit_text(
    MESSAGES["callbacks"]["about"], 
    reply_markup=back_button()
  )

