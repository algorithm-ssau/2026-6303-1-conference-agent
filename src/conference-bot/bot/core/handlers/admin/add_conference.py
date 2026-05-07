from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from pathlib import Path
# import uuid
from bot.core.states.states import AddConference
from bot.core.keyboards import back_button, ocr_buttons, data_buttons, hashtags_keyboard, post_edit_buttons, generate_post_buttons, confirm_conf_buttons, main_menu
from bot.core.constants import MESSAGES, callbacks as cb
from bot.core.callbacks import AdminCallback, FlowCallback
from bot.services.parser import PDFTextExtractor
from bot.services import AdminService, ConferenceService

from bot.services.parser.parser_service import ParserService

parser_service = ParserService()
router = Router()

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
TEMP_DIR = BASE_DIR / "temp"

@router.callback_query(AdminCallback.filter(F.action == "add_conf"))
async def add_conf(callback: CallbackQuery, state: FSMContext):
  """
    Инициирует процесс добавления конференции.

    - Проверяет права администратора
    - Очищает FSM
    - Устанавливает состояние ожидания файла
    - Просит пользователя загрузить PDF

    :param callback: CallbackQuery
    :param state: FSMContext
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
  await state.clear()
  await state.set_state(AddConference.waiting_for_file)
  
  await callback.message.edit_text(
    MESSAGES["add-conf"]["upload-file"],
    reply_markup=back_button()
  ) 


@router.message(AddConference.waiting_for_file)
async def process_file(message: Message, state: FSMContext):
  """
    Обрабатывает загруженный файл конференции.

    Шаги:
    1. Проверяет наличие документа
    2. Скачивает файл во временную директорию
    3. Передаёт файл в парсер
    4. Если парсинг успешен:
        - сохраняет parsed_data в FSM
        - форматирует данные
        - переводит состояние в проверку данных
    5. При ошибке — сообщает пользователю
    6. Удаляет временный файл

    :param message: Сообщение с документом
    :param state: FSMContext
  """
  # 1. Проверяем, что прислали файл
  if not message.document:
    await message.answer(
      "❌ Пожалуйста, отправьте PDF-файл с описанием конференции",
      reply_markup=back_button()
    )
    return
  
  TEMP_DIR.mkdir(exist_ok=True)
  
  file = await message.bot.get_file(message.document.file_id)
  local_path = TEMP_DIR / message.document.file_name
  
  await message.bot.download_file(file.file_path, local_path)
  await message.answer("📄 Файл получен. Извлекаю текст...")

  try:
    extractor = PDFTextExtractor()
    text = extractor.extract_text_smart(str(local_path))

    if not text.strip():
      await message.answer("❌ Не удалось извлечь текст")
      return

    await state.update_data(raw_text=text[:4000])  # ограничим

    await state.set_state(AddConference.text_check)

    await message.answer(
      f"📄 Проверь текст:\n\n<blockquote>{text[:1000]}</blockquote>",
      reply_markup=ocr_buttons()
    )

  except Exception as e:
    await message.answer(
      f"❌ Ошибка при обработке файла: {str(e)}",
      reply_markup=back_button()
    )
  finally:
    if local_path.exists():
      local_path.unlink()


@router.callback_query(FlowCallback.filter(F.action == "ocr_ok"))
async def ocr_ok(callback: CallbackQuery, state: FSMContext):
  """
    Подтверждает корректность распознанного текста (OCR).

    - Переводит состояние в проверку данных
    - Показывает заглушку основной информации

    :param callback: CallbackQuery
    :param state: FSMContext
  """
  await callback.answer()

  data = await state.get_data()
  text = data.get("raw_text")

  await callback.message.edit_text("🔍 Парсю данные...")

  parsed = await ConferenceService.parse_text(text)

  if not parsed:
    await callback.message.edit_text("❌ Ошибка парсинга")
    return

  await state.update_data(parsed_data=parsed)
  await state.set_state(AddConference.data_check)

  await callback.message.edit_text(
    ConferenceService.format_parsed_data(parsed),
    reply_markup=data_buttons()
  )

@router.callback_query(FlowCallback.filter(F.action == "data_ok"))
async def data_ok(callback: CallbackQuery, state: FSMContext):
  """
    Подтверждает корректность распарсенных данных.

    - Загружает список дефолтных тегов
    - Сохраняет их в FSM
    - Переводит в состояние подтверждения сохранения

    :param callback: CallbackQuery
    :param state: FSMContext
  """
  await callback.answer()
  data = await state.get_data()

  await callback.message.edit_text("✍️ Генерирую пост...")
  post_text = await ConferenceService.build_post(data)

  await state.update_data(post_text=post_text)
  await state.set_state(AddConference.post_check)

  await callback.message.edit_text(
    post_text,
    reply_markup=post_edit_buttons()
  )
    
@router.callback_query(F.data == cb.CONFIRM_SAVE_CONF)
async def confirm_save_conf(callback: CallbackQuery, state: FSMContext):
  """
    Подтверждает сохранение конференции.

    Сейчас:
    - Заглушка (TODO: сохранение в БД, проверка дубликатов)
    - Показывает сообщение об успешном сохранении
    - Предлагает сгенерировать пост

    :param callback: CallbackQuery
    :param state: FSMContext
  """
  await callback.answer()

  data = await state.get_data()

  # сохранить в БД     
  # TODO: проверка на дубликаты
  # TODO: сохранение в БД

  await callback.message.edit_text(
    MESSAGES["add-conf"]["saved-success"],
    reply_markup=generate_post_buttons()
  )    
    
    
@router.callback_query(FlowCallback.filter(F.action == "generate_post"))
async def generate_post(callback: CallbackQuery, state: FSMContext):
  """
    Генерирует текст поста на основе данных конференции.

    - Получает данные из FSM
    - Формирует текст поста через сервис
    - Сохраняет пост в FSM
    - Переводит состояние в режим редактирования поста

    :param callback: CallbackQuery
    :param state: FSMContext
  """
  await callback.answer()
  
  data = await state.get_data()
  post_text = await ConferenceService.build_post(data)
  
  await state.update_data(post_text=post_text)
  await state.set_state(AddConference.post)
  
  await callback.message.edit_text(
    post_text,
    reply_markup=post_edit_buttons(),
    parse_mode="HTML"
  )   
    
@router.callback_query(FlowCallback.filter(F.action == "ocr_edit"))
async def ocr_edit(callback: CallbackQuery):
  """
    Временный обработчик кнопки редактирования OCR ("Исправить").

    - Показывает сообщение, что функция ещё не реализована

    :param callback: CallbackQuery
  """
  await callback.answer()
  await callback.message.edit_text(
    "🛠️ **Функция редактирования в разработке**\n\n"
    "Пока что просто нажмите 'Всё верно' для продолжения тестирования.",
    reply_markup=ocr_buttons(),
    parse_mode="Markdown"
  )

@router.callback_query(FlowCallback.filter(F.action == "to_tags"))
async def to_tags(callback: CallbackQuery, state: FSMContext):
  """
    Переход к этапу выбора тегов.

    - Загружает список тегов
    - Сохраняет их в FSM
    - Переводит состояние в выбор тегов
    - Показывает клавиатуру тегов

    :param callback: CallbackQuery
    :param state: FSMContext
  """
  await callback.answer()

  tags = ConferenceService.get_default_tags()

  await state.update_data(available_tags=tags, selected_tags=[])
  await state.set_state(AddConference.hashtags)
  await callback.message.edit_text(
    "Выбери теги:",
    reply_markup=hashtags_keyboard(tags, [])
  )
  
@router.callback_query(F.data == cb.MAIN_MENU)
async def cancel_anywhere(callback: CallbackQuery, state: FSMContext):
  await state.clear()

  await callback.message.edit_text(
    "Действие отменено",
    reply_markup=main_menu(
      AdminService.is_admin(
        callback.from_user.id,
        callback.from_user.username
      )
    )
  )