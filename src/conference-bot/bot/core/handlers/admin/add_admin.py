from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.core.states.states import AddAdmin
from bot.core.keyboards import back_button, confirmation_buttons
from bot.core.constants import MESSAGES, callbacks as cb
from bot.core.callbacks import AdminCallback
from bot.services import AdminService

router = Router()


@router.callback_query(AdminCallback.filter(F.action == "add_admin")) 
async def add_admin(callback: CallbackQuery, state: FSMContext):
  """
    Инициирует процесс добавления нового администратора.

    Проверяет, является ли текущий пользователь администратором.
    Если нет — показывает alert с ошибкой.

    Если да:
    - очищает предыдущий ответ callback
    - переводит FSM в состояние ожидания username
    - отправляет сообщение с просьбой ввести username

    :param callback: CallbackQuery от нажатия кнопки "Добавить администратора"
    :param state: FSMContext для управления состоянием пользователя
  """
  if not AdminService.is_admin(callback.from_user.id):
    await callback.answer(
      MESSAGES["errors"]["for-admin-only"], 
      show_alert=True
    )
    return
  
  await callback.answer()

  await state.set_state(AddAdmin.waiting_user_name)
  await callback.message.edit_text(
    MESSAGES["add-admin"]["enter-username"],
    reply_markup=back_button()
  )

  return


@router.message(AddAdmin.waiting_user_name)
async def process_admin(message: Message, state: FSMContext):
  """
    Обрабатывает ввод username нового администратора.

    - Валидирует введённый username
    - Если невалидный — отправляет сообщение об ошибке
    - Если валидный:
      - сохраняет username в FSM
      - переводит состояние в подтверждение
      - отправляет сообщение с подтверждением добавления

    :param message: Сообщение пользователя с username
    :param state: FSMContext с данными процесса
  """
  username = message.text.strip()
  
  if not AdminService.validate_username(username):
    await message.answer(
      MESSAGES["add-admin"]["invalid-input"],
      reply_markup=back_button()
    )
    return
  
  await state.update_data(username=username)
  await state.set_state(AddAdmin.add_new_admin)
  
  confirm_text = (
    f"👤 Пользователь: {username}\n\n"
    f"{MESSAGES['add-admin']['confirm']}"
  )
  
  await message.answer(
    confirm_text,
    reply_markup=confirmation_buttons()
  )
    
    
@router.callback_query(F.data == cb.CONFIRM_ADD_ADMIN)
async def confirm_add_admin(callback: CallbackQuery, state: FSMContext):
  """
    Подтверждает добавление нового администратора.

    - Получает username из FSM
    - Если username отсутствует — показывает ошибку
    - Пытается добавить администратора через AdminService
    - При успехе — показывает сообщение об успешном добавлении
    - При ошибке — показывает дефолтную ошибку
    - Очищает FSM

    :param callback: CallbackQuery от кнопки подтверждения
    :param state: FSMContext с сохранёнными данными
  """
  await callback.answer()
  
  data = await state.get_data()
  username = data.get("username")
  
  if not username:
    await callback.message.edit_text(
      MESSAGES["errors"]["tg-user-not-found"],
      reply_markup=back_button()
    )
    return
  
  try:
    result = await AdminService.add_admin(
      username=username,
      added_by=callback.from_user.id
    )
    
    if result.get("success"):
      await callback.message.edit_text(
        MESSAGES["add-admin"]["success"],
        reply_markup=back_button()
      ) 
      
  except Exception as e:
    # logging.error(e)
    await callback.message.edit_text(
      MESSAGES["errors"]["default"],
      reply_markup=back_button()
    )
      
  await state.clear()


@router.callback_query(F.data == cb.CANCEL_ADD_ADMIN)
async def cancel_add_admin(callback: CallbackQuery, state: FSMContext):
  """
    Отменяет процесс добавления администратора.

    - Очищает состояние FSM
    - Отправляет сообщение об отмене операции

    :param callback: CallbackQuery от кнопки отмены
    :param state: FSMContext
  """
  await callback.answer()
  await state.clear()
  await callback.message.edit_text(
    MESSAGES["add-admin"]["cancel"],
    reply_markup=back_button()
  )

    