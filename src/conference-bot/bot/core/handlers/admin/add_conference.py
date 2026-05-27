from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from pathlib import Path
from html import escape
from bot.core.states.states import AddConference
from bot.core.keyboards import back_button, ocr_buttons, data_buttons, hashtags_keyboard, post_edit_buttons, generate_post_buttons, confirm_conf_buttons, main_menu
from bot.core.constants import MESSAGES, callbacks as cb
from bot.core.callbacks import AdminCallback, FlowCallback
from bot.services.parser import PDFTextExtractor
from bot.services import AdminService, ConferenceService
import logging, asyncio
from bot.services.parser.parser_service import ParserService
from bot.utils.message_manager import show_screen

import asyncio
from bot.services.search_service import SearchService

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
  """

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
  # await message.answer("📄 Файл получен. Извлекаю текст...(это может занять время)")
  await show_screen(
    message, 
    state, 
    "⌛️ Файл получен, извлекаю текст... (это может занять несколько минут)", 
    parse_mode="HTML",
    mode="new"
  )


  try:
    extractor = PDFTextExtractor()

    text = await asyncio.to_thread(extractor.extract_text_smart, str(local_path))

    if not text.strip():
      await message.answer("❌ Не удалось извлечь текст. Файл пуст")
      return
    
    await state.update_data(raw_text=text)

    from io import BytesIO
    from aiogram.types import BufferedInputFile

    file = BufferedInputFile(
      text.encode("utf-8"),
      filename="ocr_text.txt"
    )
    file.name = "ocr_text.txt"

    await message.answer_document(file, caption="Распознанный текст целиком")
    preview = f"{escape(text[:100])}\n...\n{escape(text[-100:])}"


    # safe_text = escape(text[:1000])
    try:
      await show_screen(
        message, 
        state, 
        f"📄 Проверьте распознанный текст.\nПревью:\n<blockquote>{preview}</blockquote>",
        reply_markup=ocr_buttons(), 
        parse_mode="HTML",
        mode="new"
      )

    except Exception as e:
      logging.warning(f"Таймаут соединения после OCR, отправляем повторно: {e}")
      await message.answer(
        f"📄 Проверьте распознанный текст.\nПревью:\n<blockquote>{preview}</blockquote>",
        reply_markup=ocr_buttons(),
        parse_mode="HTML"
      )

  except Exception as e:
    logging.error(f"Ошибка OCR: {e}")
    try:
      await message.answer(
        f"❌ Ошибка при обработке файла: {str(e)}",
        reply_markup=back_button()
      )
    except Exception:
      pass
  finally:
    if local_path.exists():
      local_path.unlink()


@router.callback_query(FlowCallback.filter(F.action == "ocr_ok"))
async def ocr_ok(callback: CallbackQuery, state: FSMContext):
  await callback.answer()
  data = await state.get_data()
  text = data.get("raw_text")

  if not text:
    await callback.message.answer("❌ Текст не найден. Попробуйте заново.")
    return

  await show_screen(callback, state, "⌛️ Парсю данные...", mode="new")
  
  try:
    # parsed = await ConferenceService.parse_text(text)

    from pydantic import ValidationError
    from bot.services.parser.models import EventData

    parsed_raw = await ConferenceService.parse_text(text)

    try:
      parsed = EventData(**parsed_raw).model_dump()
    except ValidationError as e:
      await callback.message.answer(
        f"❌ Ошибка в структуре данных:\n\n<pre>{escape(str(e))}</pre>",
        parse_mode="HTML"
      )
      return


    if not parsed:
      try:
        await callback.message.edit_text("❌ Ошибка парсинга: не удалось извлечь данные.")
      except Exception:
        await callback.message.answer("❌ Ошибка парсинга.")
      return
    
    # await state.update_data(parsed_data=parsed)
    await state.update_data(
      parsed_data=parsed,
      last_valid_parsed=parsed
    )
    await state.set_state(AddConference.data_check)

    response_text = ConferenceService.format_parsed_data(parsed)
    
    # Пробуем отредактировать старое сообщение
    try:
      await show_screen(callback, state, response_text, reply_markup=data_buttons(), mode="edit")
    except Exception as e:
      # Если TCP-соединение отвалилось (WinError 121), отправляем ответ новым сообщением
      logging.warning(f"Не удалось отредактировать сообщение, отправляю новое: {e}")
      await callback.message.answer(
        response_text,
        reply_markup=data_buttons()
      )
  except Exception as e:
    logging.error(f"Сбой в процессе парсинга: {e}")
    await callback.message.answer(
      "❌ Произошла неизвестная ошибка при обращении к нейросетям.",
      reply_markup=back_button()
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
  parsed = data.get("parsed_data")

  
  if parsed:
    await show_screen(callback, state, "⏳ Сохраняю данные и считаю векторы...", mode="new")
    # Собираем строку из фактов
    text_to_encode = f"{parsed.get('event_name', '')}. {parsed.get('event_type', '')}. Аудитория: {parsed.get('target_audience', '')}. Организатор: {parsed.get('organizer', '')}"
    
    # Считаем вектор в отдельном потоке
    emb_bytes = await asyncio.to_thread(SearchService.get_embedding_bytes, text_to_encode)
    
    # Сохраняем в БД уже вместе с вектором
    db_id = ConferenceService.save_to_db(parsed, emb_bytes)
    if db_id:
      await state.update_data(db_id=db_id)
  
  await show_screen(
    callback, 
    state, 
    "✅ Данные успешно сохранены в базу!\n\nПереходим к созданию поста?", 
    reply_markup=generate_post_buttons(), 
    mode="new"
  )


@router.callback_query(FlowCallback.filter(F.action == "data_edit"))
async def data_edit(callback: CallbackQuery, state: FSMContext):
    try:
      await callback.answer()
    except Exception:
      pass
    
    data = await state.get_data()
    parsed = data.get("parsed_data", {})

    text = ConferenceService.format_parsed_data(parsed)

    await state.set_state(AddConference.waiting_for_data_edit)

    await show_screen(
        callback,
        state,
        "✏️ Отредактируйте данные и отправьте полный текст. Для корректной обработки соблюдайте синтаксис, как здесь:\n\n"
        f"<pre>{escape(text)}</pre>",
        parse_mode="HTML",
        mode="edit"
    )


@router.message(AddConference.waiting_for_data_edit)
async def receive_data_edit(message: Message, state: FSMContext):
  text = message.text

  if not text:
    await message.answer("❌ Текст не должен быть пустым")
    return

  try:
    parsed_partial = parse_edited_text(text)

    data = await state.get_data()
    old_data = data.get("parsed_data", {})

    # объединяем старые и новые данные
    merged = {**old_data, **parsed_partial}

    from pydantic import ValidationError
    from bot.services.parser.models import EventData

    try:
      validated = EventData(**merged).model_dump()
    except ValidationError as e:
      await message.answer(
        f"❌ Ошибка в данных:\n\n<pre>{escape(str(e))}</pre>",
        parse_mode="HTML"
      )
      return

    await state.update_data(
      parsed_data=validated,
      last_valid_parsed=validated
    )

    response_text = ConferenceService.format_parsed_data(validated)

    await state.set_state(AddConference.data_check)

    await show_screen(
      message,
      state,
      response_text,
      reply_markup=data_buttons(),
      mode="new"
    )

  except Exception as e:
    await message.answer("❌ Ошибка обработки. Попробуйте снова.")


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

  # Добавляем лоадер, так как генерация занимает время
  await show_screen(callback, state, "⌛️Генерирую пост, подождите...", mode="edit")
  
  data = await state.get_data()

  try:
    post_text = await ConferenceService.build_post(data)
    
    if not post_text:
      try:
        await callback.message.edit_text("❌ Ошибка генерации поста. Не удалось создать пост.")
      except Exception:
        await callback.message.answer("❌ Ошибка генерации")
      return

    await state.update_data(post_text=post_text)
    await state.set_state(AddConference.post_check)
    
    try:
      await show_screen(callback, state, post_text, reply_markup=post_edit_buttons(), parse_mode="HTML", mode="edit") 
    except Exception as e:
      # Если TCP-соединение отвалилось (WinError 121), отправляем ответ новым сообщением
      logging.warning(f"Не удалось отредактировать сообщение, отправляю новое: {e}")
      await callback.message.answer(
        post_text,
        reply_markup=post_edit_buttons(),
        parse_mode="HTML"
      )
     
  except Exception as e:
    logging.error(f"Сбой в процессе генерации поста: {e}")
    await callback.message.answer(
      "❌ Произошла неизвестная ошибка при обращении к нейросетям при попытке генерации поста.",
      reply_markup=back_button()
    ) 


@router.callback_query(FlowCallback.filter(F.action == "post_edit"))
async def post_edit(callback: CallbackQuery, state: FSMContext):
  await callback.answer()

  await state.set_state(AddConference.waiting_for_post_edit)

  await show_screen(
    callback,
    state,
    "✏️ Отправьте новый текст поста одним сообщением",
    mode="edit"
  )


@router.callback_query(FlowCallback.filter(F.action == "ocr_edit"))
async def ocr_edit(callback: CallbackQuery, state: FSMContext):
  """
    Временный обработчик кнопки редактирования OCR ("Исправить").

    - Показывает сообщение, что функция ещё не реализована

    :param callback: CallbackQuery
  """
  await callback.answer()
  await state.set_state(AddConference.waiting_for_text_edit)
  await show_screen(
    callback,
    state,
    "✏️ Отправьте исправленный текст (целиком) в формате .txt",
    mode="edit"
  )



@router.message(AddConference.waiting_for_text_edit)
async def receive_edited_text(message: Message, state: FSMContext):
  if not message.document:
    await message.answer("❌ Пришлите .txt файл")
    return

  if not message.document.file_name.endswith(".txt"):
    await message.answer("❌ Файл должен быть .txt")
    return

  try:
    file = await message.bot.get_file(message.document.file_id)

    content = await message.bot.download_file(file.file_path)
    text = content.read().decode("utf-8") if hasattr(content, "read") else content.decode("utf-8")

    if not text.strip():
      raise ValueError("Пустой файл")

    await state.update_data(raw_text=text)
    await state.set_state(AddConference.text_check)

    preview = f"{escape(text[:500])}\n...\n{escape(text[-500:])}"

    await show_screen(
      message,
      state,
      f"📄 Обновлённый текст:\n\n<blockquote>{preview}</blockquote>",
      reply_markup=ocr_buttons(),
      parse_mode="HTML",
      mode="new"
    )


  except Exception as e:
    await message.answer(
      "❌ Ошибка чтения файла. Попробуйте снова или отмените.",
      reply_markup=ocr_buttons()
    )


@router.message(AddConference.waiting_for_post_edit)
async def receive_post_edit(message: Message, state: FSMContext):
  # Используем html_text, чтобы захватить Telegram-форматирование от пользователя
  text = message.html_text 
  if not text or not text.strip():
    await message.answer("❌ Текст не должен быть пустым")
    return
  try:
    # Ставим текст напрямую без escape и blockquote
    formatted_post = (
      MESSAGES["publish-post"]["post-preview"]
      + "\n\n" + text
    )
    data = await state.get_data()
    selected_tags = data.get("selected_tags", [])
    if selected_tags:
      formatted_post += "\n\n" + " ".join(selected_tags)
    await state.update_data(post_text=text)
    await state.set_state(AddConference.post_check)
    await show_screen(
      message,
      state,
      formatted_post,
      reply_markup=post_edit_buttons(),
      parse_mode="HTML",
      mode="new"
    )
  except Exception:
    await message.answer(
      "❌ Ошибка обработки текста. Попробуйте снова.",
      reply_markup=post_edit_buttons()
    )


@router.callback_query(FlowCallback.filter(F.action == "regen_post"))
async def regen_post(callback: CallbackQuery, state: FSMContext):
  await callback.answer()

  await show_screen(callback, state, "⏳ Перегенерирую пост...", mode="edit")

  data = await state.get_data()

  try:
    post_text = await ConferenceService.build_post(data)

    if not post_text:
      await callback.message.answer("❌ Не удалось перегенерировать пост")
      return

    await state.update_data(post_text=post_text)

    await show_screen(
      callback,
      state,
      post_text,
      reply_markup=post_edit_buttons(),
      parse_mode="HTML",
      mode="edit"
    )

  except Exception as e:
    logging.error(f"Ошибка перегенерации: {e}")
    await callback.message.answer("❌ Ошибка при перегенерации")


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
  try:
    await callback.answer()
  except Exception:
    pass

  try:
    await show_screen(callback, state, "⏳ Подбираю подходящие теги...", mode="new")
  except Exception:
    pass
  
  data = await state.get_data()
  post_text = data.get("post_text", "")

  try:
    # Вызываем наш метод со смарт-тегами
    tags = await ConferenceService.get_smart_tags(post_text)
    await state.update_data(available_tags=tags, selected_tags=[])
    await state.set_state(AddConference.hashtags)
    # Пробуем отредактировать старое сообщение с часами
    try:
      await callback.message.edit_text(
        "Выбери теги:",
        reply_markup=hashtags_keyboard(tags, [])
      )
    except Exception as e:
      # Если TCP-соединение отвалилось (WinError 121), отправляем новым сообщением
      logging.warning(f"Таймаут соединения, отправляю новым сообщением: {e}")
      await show_screen(callback, state, "Выбери теги:", reply_markup=hashtags_keyboard(tags, []), mode="edit")
  except Exception as e:
    logging.error(f"Ошибка при подборе тегов: {e}")
    error_msg = "❌ Произошла сетевая ошибка при генерации тегов. Пожалуйста, вернитесь в меню."
    
    try:
      await callback.message.edit_text(
        error_msg, 
        reply_markup=main_menu(True)
      )
    except Exception:
      await callback.message.answer(
        error_msg, 
        reply_markup=main_menu(True)
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


def parse_edited_text(text: str) -> dict:
  mapping = {
    "Название": "event_name",
    "Формат": "event_type",
    "Организатор": "organizer",
    "Даты": "dates",
    "Масштаб": "status",
    "Дедлайны": "deadlines",
    "Ссылки": "links",
    "Место": "location",
    "РИНЦ": "rsci",
    "Формат проведения": "format",
    "Целевая аудитория": "target_audience",
    "Ключевые слова": "topics"
  }

  result = {}

  for line in text.split("\n"):
    if ":" not in line:
      continue

    key, value = line.split(":", 1)

    # Избавляемся от дефисов, маркеров списков и пробелов
    key = key.lstrip("-•* ").strip()
    value = value.strip()

    if key in mapping:
      field = mapping[key]

      # Обработка сложных типов (Pydantic упадет, если в list отправить строку)
      if field == "deadlines" and value:
        deadlines_list = []
        for item in value.split(";"):
          if "-" in item:
            date, desc = item.split("-", 1)
            deadlines_list.append({"date": date.strip(), "description": desc.strip()})
        result[field] = deadlines_list
      elif field == "links" and value:
        links_list = []
        for item in value.split(";"):
          if "-" in item:
            url, desc = item.split("-", 1)
            links_list.append({"url": url.strip(), "description": desc.strip()})
        result[field] = links_list
      elif field == "topics" and value:
        clean_val = value.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
        result[field] = [v.strip() for v in clean_val.split(",") if v.strip()]
      elif field == "rsci":
        result[field] = value.lower() in ("true", "да", "1", "yes")
      else:
        result[field] = value
  return result