from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

from bot.core.callbacks import TagCallback, FlowCallback
from bot.core.states.states import AddConference
from bot.core.keyboards import post_buttons, main_menu
from bot.config import CHANNEL_ID

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

  try:
    await callback.message.edit_text(
      final_post,
      reply_markup=post_buttons()
    )
  except Exception as e:
    logging.warning(f"edit_text упал, отправляю новым сообщением: {e}")
    await callback.message.answer(
        final_post,
        reply_markup=post_buttons()
    )


@router.callback_query(FlowCallback.filter(F.action == "publish"))
async def publish(callback: CallbackQuery, state: FSMContext):
  """
    Публикует пост в канал.
  """
  await callback.answer()
  data = await state.get_data()
  final_post = data.get("final_post")

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
      await callback.message.edit_text(
        "✅ Пост успешно опубликован в канал!",
        reply_markup=main_menu(True)
      )
    except Exception as e:
      logging.warning(f"Не удалось отредактировать сообщение: {e}")
      await callback.message.answer(
        "✅ Пост успешно опубликован в канал!",
        reply_markup=main_menu(True)
      )

  except Exception as e:
    logging.error(f"Ошибка публикации в канал: {e}")
    await callback.message.edit_text(
      f"❌ Ошибка публикации: {e}",
      reply_markup=main_menu(True)
    )
