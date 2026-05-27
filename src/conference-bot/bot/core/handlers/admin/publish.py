from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

from bot.core.callbacks import TagCallback, FlowCallback
from bot.core.states.states import AddConference
from bot.core.keyboards import post_buttons, main_menu
from bot.config import CHANNEL_ID
from bot.utils import show_screen
from bot.services.search_service import SearchService

import asyncio

router = Router()

@router.callback_query(TagCallback.filter(F.action == "finish"))
async def finish_tags(callback: CallbackQuery, state: FSMContext):
  """
    Завершает выбор тегов.

    - Генерирует финальный текст поста
    - Сохраняет его в FSM
    - Переводит в состояние предпросмотра поста

    :param callback: CallbackQuery
    :param state: FSMContext
  """
  await callback.answer()

  data = await state.get_data()

  post = data.get("post_text")
  tags = data.get("selected_tags", [])

  final_post = post + "\n\n" + " ".join(tags)

  await state.update_data(final_post=final_post)
  await state.set_state(AddConference.preview)
  display_text = f"Финальный вид поста (готово к публикации):\n\n{final_post}"

  try:
    await show_screen(callback, state, display_text, reply_markup=post_buttons(), parse_mode="HTML", mode="edit")
    
  except Exception as e:
    logging.warning(f"edit_text упал, отправляю новым сообщением: {e}")
    await callback.message.answer(
      await callback.message.answer(
        display_text, 
        reply_markup=post_buttons(), 
        parse_mode="HTML"
      )
    )


@router.callback_query(FlowCallback.filter(F.action == "publish"))
async def publish(callback: CallbackQuery, state: FSMContext):
  """
    Публикует пост в канал.
  """
  await callback.answer()
  data = await state.get_data()

  # ??? 
  db_id = data.get("db_id")
  selected_tags = data.get("selected_tags", [])
  final_post = data.get("final_post")


  if db_id and selected_tags:
    await show_screen(callback, state, "⏳ Публикую...", mode="new")

  if not final_post:
    await callback.message.edit_text(
      "❌ Ошибка: нет текста для публикации.", 
      reply_markup=main_menu(True)
    )
    return

  try:
    # Отправляем сообщение в канал
    await callback.bot.send_message(
      chat_id=CHANNEL_ID,
      text=final_post,
      parse_mode="HTML"
    )
    await state.clear()
    try:
      await show_screen(callback, state, "✅ Пост успешно опубликован в канал!", reply_markup=main_menu(True), mode="new")
    except Exception as e:
      logging.warning(f"Не удалось отредактировать сообщение: {e}")
      await show_screen(callback, state, "✅ Пост успешно опубликован в канал!", reply_markup=main_menu(True), mode="new")

  except Exception as e:
    logging.error(f"Ошибка публикации в канал: {e}")
    await callback.message.edit_text(
      f"❌ Ошибка публикации: {e}",
      reply_markup=main_menu(True)
    )
