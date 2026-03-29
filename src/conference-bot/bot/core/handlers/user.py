from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.core.keyboards.common import main_menu, back_button
from bot.core.keyboards.user import search_buttons
from bot.core.states.states import Search
from bot.config import ADMIN_IDS

router = Router()





@router.message(F.text == "/start")
async def start(message: Message):
  is_admin = message.from_user.id in ADMIN_IDS
  await message.answer("Бот для поиска научных конференций.\n\nВыберите действие:", reply_markup=main_menu(is_admin))


@router.callback_query(F.data == "main_menu")
async def main_menu_handler(callback: CallbackQuery, state: FSMContext):
  await state.clear()
  
  is_admin = callback.from_user.id in ADMIN_IDS
  
  await callback.message.edit_text("Главное меню", reply_markup=main_menu(is_admin))


@router.callback_query(F.data == "about")
async def about(callback: CallbackQuery):
  await callback.message.edit_text("Заглушка: описание проекта.", reply_markup=back_button())


@router.callback_query(F.data == "search")
async def search(callback: CallbackQuery, state: FSMContext):
  await state.set_state(Search.waiting_query)
  await callback.message.edit_text("Введите тему или название работы:", reply_markup=back_button())


@router.message(Search.waiting_query)
async def process_search(message: Message):
  await message.answer("Заглушка:\n\n1️⃣ Conf A\n2️⃣ Conf B\n3️⃣ Conf C", reply_markup=search_buttons())