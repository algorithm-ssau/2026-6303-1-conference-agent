from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.core.constants import callbacks as cb
from bot.core.keyboards.common import main_menu
from bot.core.keyboards.common import back_button
from bot.config import ADMIN_IDS

router = Router()

# Общие обработчики
@router.callback_query(F.data == cb.MAIN_MENU)
async def main_menu_handler(callback: CallbackQuery, state: FSMContext):
  await state.clear()
  is_admin = callback.from_user.id in ADMIN_IDS
  await callback.message.edit_text(
    "Главное меню", 
    reply_markup=main_menu(is_admin)
  )

@router.callback_query(F.data == cb.ABOUT)
async def about_handler(callback: CallbackQuery):
  await callback.message.edit_text(
    "Справочная информация: ...", 
    reply_markup=back_button()
  )

# Обработчик отмены (общий для всех состояний)
@router.callback_query(F.data == cb.MAIN_MENU)
async def cancel_handler(callback: CallbackQuery, state: FSMContext):
  await state.clear()
  is_admin = callback.from_user.id in ADMIN_IDS
  await callback.message.edit_text(
    "Действие отменено", 
    reply_markup=main_menu(is_admin)
  )