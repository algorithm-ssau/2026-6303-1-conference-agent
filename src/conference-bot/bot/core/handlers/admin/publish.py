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
  post_text = ConferenceService.build_post(data)
  await state.update_data(post_text=post_text)
  await state.set_state(AddConference.post)
  await callback.message.edit_text(
    post_text,
    reply_markup=post_buttons(),
    parse_mode="HTML"
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
  
  # 1. Достаем данные из FSM
  data = await state.get_data()
  # conference_data = data.get("conference_data")
  parsed = data.get("parsed_data")

  try:
    # 2. Сохраняем в БД
    if parsed:
      ConferenceService.save_to_db(parsed)

    # 3. (потом сюда можно воткнуть публикацию поста)
    # await ConferenceService.publish_post(...)

    # 4. Чистим состояние
    await state.clear()

    # 5. Ответ пользователю
    await callback.message.edit_text(
      MESSAGES["publish-post"]["success"],
      reply_markup=main_menu(
        AdminService.is_admin(callback.from_user.id)
      )
    )

  except Exception as e:
    await callback.message.edit_text(
      f"❌ Ошибка при сохранении: {str(e)}",
      reply_markup=main_menu(
          AdminService.is_admin(callback.from_user.id)
      )
    )