from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards.common import back_button, main_menu
from bot.keyboards.admin import (
  ocr_buttons,
  data_buttons,
  hashtag_buttons,
  post_buttons
)
from bot.states.states import AddConference
from bot.config import ADMIN_IDS

router = Router()


'''
  Проверка на вход админом
'''
def is_admin(user_id):
  return user_id in ADMIN_IDS


@router.callback_query(F.data == "add_conf")
async def add_conf(callback: CallbackQuery, state: FSMContext):
  if not is_admin(callback.from_user.id): 
    return

  await state.set_state(AddConference.waiting_for_file)
  await callback.message.edit_text("Пришлите файл (заглушка).", reply_markup=back_button())


@router.message(AddConference.waiting_for_file)
async def process_file(message: Message, state: FSMContext):
  await state.set_state(AddConference.ocr_check)
  await message.answer("Заглушка OCR:\n\nТекст...", reply_markup=ocr_buttons())


@router.callback_query(F.data == "ocr_ok")
async def ocr_ok(callback: CallbackQuery, state: FSMContext):
  await state.set_state(AddConference.data_check)
  await callback.message.edit_text("Название: ...\nДата: ...\nДедлайн: ...", reply_markup=data_buttons())


@router.callback_query(F.data == "data_ok")
async def data_ok(callback: CallbackQuery, state: FSMContext):
  await state.set_state(AddConference.hashtags)
  await callback.message.edit_text("#hashtag1 #hashtag2 #hashtag3", reply_markup=hashtag_buttons())


@router.callback_query(F.data == "to_post")
async def to_post(callback: CallbackQuery, state: FSMContext):
  await state.set_state(AddConference.post)
  await callback.message.edit_text("Заглушка поста...", reply_markup=post_buttons())


@router.callback_query(F.data == "publish")
async def publish(callback: CallbackQuery, state: FSMContext):
  await state.clear()
  await callback.message.edit_text("Пост опубликован (заглушка).", reply_markup=main_menu(True))