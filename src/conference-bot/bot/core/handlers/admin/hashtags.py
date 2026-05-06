from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.core.keyboards import hashtags_keyboard, back_button
from bot.core.constants import MESSAGES
from bot.core.callbacks import TagCallback
from bot.core.states.states import AddConference
from bot.services import ConferenceService

router = Router()

@router.callback_query(TagCallback.filter(F.action == "toggle"))
async def toggle_tag_handler(callback: CallbackQuery, callback_data: TagCallback, state: FSMContext):
  """
    Переключает состояние тега (выбран/не выбран).
    - Обновляет список выбранных тегов
    - Перерисовывает клавиатуру

    :param callback: CallbackQuery
    :param callback_data: данные callback с тегом
    :param state: FSMContext
  """
  await callback.answer()
  
  if not callback_data.tag:
    return
  
  data = await state.get_data()
  data = ConferenceService.toggle_tag(data, callback_data.tag)
  
  await state.update_data(data)
  await callback.message.edit_reply_markup(
    reply_markup=hashtags_keyboard(
      data.get("available_tags", []),
      data.get("selected_tags", [])
    )
  )


@router.callback_query(TagCallback.filter(F.action == "add"))
async def add_tag_handler(callback: CallbackQuery, state: FSMContext):
  """
    Инициирует добавление пользовательского тега.
    - Переводит FSM в состояние ввода тега
    - Просит пользователя ввести тег

    :param callback: CallbackQuery
    :param state: FSMContext
  """
  await callback.answer()
  await state.set_state(AddConference.hashtags)
  await callback.message.edit_text(
    MESSAGES["add-tags"]["enter-tag"],
    reply_markup=back_button()
  )


@router.message(AddConference.hashtags)
async def process_new_tag(message: Message, state: FSMContext):
  """
    Обрабатывает ввод нового пользовательского тега.
    - Добавляет тег в список доступных
    - Обновляет FSM
    - Показывает обновлённую клавиатуру тегов

    :param message: сообщение с тегом
    :param state: FSMContext
  """
  new_tag = message.text.strip()
  data = await state.get_data()
  data = ConferenceService.add_tag(data, new_tag)
  
  await state.update_data(data)
  await message.answer(
    MESSAGES["add-tags"]["user-tag-added"],
    reply_markup=hashtags_keyboard(
      data.get("available_tags", []),
      data.get("selected_tags", [])
    )
  )