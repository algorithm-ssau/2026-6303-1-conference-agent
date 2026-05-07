from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.core.constants import callbacks as cb, MESSAGES
from bot.core.keyboards import main_menu, back_button, search_buttons, search_buttons_simple
from bot.core.states.states import Search
from bot.services import AdminService,SearchService


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
    await message.answer(
      MESSAGES["errors"]["enter-search-request"],
      reply_markup=back_button()
    )

    return
  

  await state.update_data(last_query=query, current_offset=0)
  results = await search_service.search(query, limit=5, offset=0)
  
  await state.update_data(total_results=results["total"])
  formatted_results = SearchService.format_search_results(results["results"])
  
  has_more = results["has_more"] and results["total"] > 5
  
  await message.answer(
    formatted_results,
    reply_markup=search_buttons(has_more=has_more, offset=results["offset"] + results["limit"]),
    parse_mode="HTML"
  )

  
@router.callback_query(F.data.startswith(cb.MORE))
async def show_more(callback: CallbackQuery, state: FSMContext):
  """
    Загружает следующую страницу результатов поиска.

    - Извлекает offset из callback
    - Выполняет повторный поиск
    - Обновляет сообщение с результатами
    - Обновляет кнопки пагинации

    :param callback: CallbackQuery
    :param state: FSMContext
  """
  await callback.answer()
  
  try:
    offset = SearchService.parse_offset(callback.data)
  except (IndexError, ValueError):
    offset = 0
  
  data = await state.get_data()
  query = data.get("last_query", "")
  total_results = data.get("total_results", 0)
  
  if not query:
    await callback.message.edit_text(
      MESSAGES["errors"]["search-request-not-found"],
      reply_markup=search_buttons_simple()
    )
    return
  
  results = await search_service.search(query, limit=5, offset=offset)
  formatted_results = SearchService.format_search_results(results["results"])
  has_more = offset + results["limit"] < total_results
  
  await callback.message.edit_text(
    formatted_results,
    reply_markup=search_buttons(
      has_more=has_more,
      offset=offset + results["limit"]
    ),
    parse_mode="HTML"
  )
