from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from pathlib import Path
# import uuid
from bot.core.states.states import AddConference
from bot.core.keyboards import back_button, ocr_buttons, data_buttons, hashtags_keyboard, post_edit_buttons, generate_post_buttons, confirm_conf_buttons
from bot.core.constants import MESSAGES, callbacks as cb
from bot.core.callbacks import AdminCallback, FlowCallback
from bot.services import AdminService, ConferenceService

from bot.services.parser.parser_service import ParserService

parser_service = ParserService()
router = Router()

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
TEMP_DIR = BASE_DIR / "temp"

@router.callback_query(AdminCallback.filter(F.action == "add_conf"))
async def add_conf(callback: CallbackQuery, state: FSMContext):
    if not AdminService.is_admin(callback.from_user.id):
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
     # 1. Проверяем, что прислали файл
    if not message.document:
        await message.answer(
            "❌ Пожалуйста, отправьте PDF-файл с описанием конференции",
            reply_markup=back_button()
        )
        return
    
    TEMP_DIR.mkdir(exist_ok=True)
    document = message.document
    
    file = await message.bot.get_file(document.file_id)
    file_path = file.file_path
    local_path = TEMP_DIR / document.file_name
    # local_path = TEMP_DIR / f"{uuid.uuid4()}_{document.file_name}"

    await message.bot.download_file(
        file_path, 
        destination=local_path)
    await message.answer("📄 Файл получен. Распознаю текст...")

    # data = parser_service.parse_pdf(file_path)

    # if not data:
    #     await message.answer("❌ Не удалось распознать данные")
    #     return

    # await state.update_data(parsed_data=data)
    # await state.set_state(AddConference.ocr_check)
    # await message.answer(
    #     MESSAGES["add-conf"]["ocr-stub"]
    # )
    try:
        # 4. Запускаем парсер
        parsed_data = await ConferenceService.parse_file(local_path)

        if not parsed_data:
            await message.answer(
                "❌ Не удалось извлечь данные из файла",
                reply_markup=back_button()
            )
            return

        # 5. Сохраняем в FSM
        await state.update_data(parsed_data=parsed_data)

        # 6. Форматируем для показа
        text = ConferenceService.format_parsed_data(parsed_data)

        # 7. Переход в следующий шаг
        await state.set_state(AddConference.data_check)

        await message.answer(
            text,
            reply_markup=data_buttons()
        )

    except Exception as e:
        await message.answer(
            f"❌ Ошибка при обработке файла: {str(e)}",
            reply_markup=back_button()
        )


@router.callback_query(FlowCallback.filter(F.action == "ocr_ok"))
async def ocr_ok(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AddConference.data_check)
    await callback.message.edit_text(
        MESSAGES["add-conf"]["main-info_stub"],
        reply_markup=data_buttons(),
        parse_mode="HTML"
    )


@router.callback_query(FlowCallback.filter(F.action == "data_ok"))
async def data_ok(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    tags = ConferenceService.get_default_tags()
    await state.update_data(available_tags=tags, selected_tags=[])
    await state.set_state(AddConference.confirm_save)
    await callback.message.edit_text(
        MESSAGES["add-conf"]["confirm-save"],
        reply_markup = confirm_conf_buttons()
    )
    
@router.callback_query(F.data == cb.CONFIRM_SAVE_CONF)
async def confirm_save_conf(callback: CallbackQuery, state: FSMContext):
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
    await callback.answer()
    
    data = await state.get_data()
    post_text = ConferenceService.build_post(data)
    
    await state.update_data(post_text=post_text)
    await state.set_state(AddConference.post)
    
    await callback.message.edit_text(
        post_text,
        reply_markup=post_edit_buttons(),
        parse_mode="HTML"
    )   
    
@router.callback_query(FlowCallback.filter(F.action == "ocr_edit"))
async def ocr_edit(callback: CallbackQuery):
    """Временный обработчик для кнопки 'Исправить'"""
    await callback.answer()
    await callback.message.edit_text(
        "🛠️ **Функция редактирования в разработке**\n\n"
        "Пока что просто нажмите 'Всё верно' для продолжения тестирования.",
        reply_markup=ocr_buttons(),
        parse_mode="Markdown"
    )

@router.callback_query(FlowCallback.filter(F.action == "to_tags"))
async def to_tags(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    tags = ConferenceService.get_default_tags()
    await state.update_data(available_tags=tags, selected_tags=[])
    await state.set_state(AddConference.hashtags)
    
    await callback.message.edit_text(
        MESSAGES["add-conf"]["add-tags"],
        reply_markup=hashtags_keyboard(tags, [])
    )
