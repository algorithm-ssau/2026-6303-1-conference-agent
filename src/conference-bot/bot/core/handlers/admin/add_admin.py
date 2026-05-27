from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.core.states.states import AddAdmin
from bot.core.keyboards import back_button, confirmation_buttons, main_menu
from bot.core.constants import MESSAGES, callbacks as cb
from bot.core.callbacks import AdminCallback
from bot.utils.message_manager import show_success
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
  if not AdminService.is_admin(
    callback.from_user.id,
    callback.from_user.username
    ):
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
  username_raw = message.text or ""
  username = normalize_username(username_raw)

  
  if not AdminService.validate_username(username):
    await message.answer(
      MESSAGES["add-admin"]["invalid-input"],
      reply_markup=back_button()
    )
    return
  
  # вынести сообщение в месседжес
  if username in [str(x) for x in AdminService.get_admins()]:
    await message.answer(
      "⚠️ Этот пользователь уже администратор",
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
    await state.clear()
    return
  
  try:
    result = await AdminService.add_admin(
      username=username,
      added_by=callback.from_user.id
    )
    
    if not result.get("success"):
      if result.get("reason") == "already_exists":
        await callback.message.edit_text(
          f"⚠️ @{username} уже администратор",
          reply_markup=back_button()
        )
        return
    
    await callback.message.edit_text(
      f"✅ @{username} теперь администратор",
      reply_markup=main_menu(True)
    )
    
  except PermissionError:
    await callback.message.edit_text(
      MESSAGES["errors"]["for-admin-only"],
      reply_markup=back_button()
    )
      
  except Exception:
    await callback.message.edit_text(
      MESSAGES["errors"]["default"],
      reply_markup=back_button()
    )
      
  await state.clear()

# перенести потом в утилиту
def normalize_username(username: str) -> str:
  username = username.strip()
  if username.startswith("@"):
    username = username[1:]
  return username.lower()
    