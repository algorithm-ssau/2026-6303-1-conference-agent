from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.core.constants import callbacks as cb, MESSAGES
from bot.core.keyboards import main_menu, back_button, search_buttons_simple
from bot.core.states.states import Search
from bot.services import AdminService,SearchService
from bot.utils.message_manager import show_screen


router = Router()
search_service = SearchService()

@router.message(F.text == "/start")
async def start(message: Message):
  """
    Обработчик команды /start.

    - Отправляет приветственное сообщение
    - Показывает главное меню (с учётом роли пользователя)

    :param message: Message
  """
  await message.answer(
    MESSAGES["main-menu"]["start-msg"],
    reply_markup=main_menu(AdminService.is_admin(message.from_user.id))
  )


@router.callback_query(F.data == cb.SEARCH)
async def search(callback: CallbackQuery, state: FSMContext):
  """
    Инициирует поиск конференций.

    - Переводит FSM в состояние ожидания запроса
    - Просит пользователя ввести тему поиска

    :param callback: CallbackQuery
    :param state: FSMContext
  """
  await state.set_state(Search.waiting_query)
  await callback.message.edit_text(
    MESSAGES["search-conf"]["enter-topic"],
    reply_markup=back_button()
  )


@router.message(Search.waiting_query)
async def process_search(message: Message, state: FSMContext):
  """
    Обрабатывает поисковый запрос пользователя.

    - Валидирует ввод
    - Выполняет поиск через SearchService
    - Сохраняет данные пагинации в FSM
    - Отправляет первые результаты

    :param message: Message с текстом запроса
    :param state: FSMContext
  """
  query = message.text.strip()
  
  if not query:
    await show_screen(
      message, 
      state, 
      MESSAGES["errors"]["enter-search-request"], 
      reply_markup=back_button(), 
      mode="new")
    return
  
  # Отправляем лоадер новым сообщением, стирая кнопки у прошлого

  await show_screen(
    message, 
    state, 
    "🔍 Ищу подходящие конференции (это займет пару секунд)…", 
    mode="new"
  ) 
  
  # получаем топ-3 результатов
  results = await search_service.search(query, limit=3)
  formatted_results = SearchService.format_search_results(results)
  
  # Заменяем лоадер на результаты
  await show_screen(
    message, state,
    formatted_results,
    reply_markup=search_buttons_simple(),
    parse_mode="HTML",
    mode="edit"
  )

  