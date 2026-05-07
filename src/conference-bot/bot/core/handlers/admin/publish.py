from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.core.constants import MESSAGES
from bot.core.callbacks import TagCallback, FlowCallback
from bot.core.states.states import AddConference
from bot.core.keyboards import post_buttons, main_menu
from bot.services import ConferenceService, AdminService

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

  await callback.message.edit_text(
    final_post,
    reply_markup=post_buttons()
  )


@router.callback_query(FlowCallback.filter(F.action == "publish"))
async def publish(callback: CallbackQuery, state: FSMContext):
  """
    Публикует конференцию.

    - Получает данные из FSM
    - Сохраняет конференцию в БД
    - (в будущем) публикует пост
    - Очищает FSM
    - Возвращает пользователя в главное меню

    :param callback: CallbackQuery
    :param state: FSMContext
  """
  await callback.answer()

  data = await state.get_data()
  parsed = data.get("parsed_data")

  try:
    if parsed:
      ConferenceService.save_to_db(parsed)

    await state.clear()

    await callback.message.edit_text(
      "✅ Опубликовано",
      reply_markup=main_menu(True)
    )

  except Exception as e:
    await callback.message.edit_text(f"❌ Ошибка: {e}")
