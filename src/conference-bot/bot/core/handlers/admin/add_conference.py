from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.core.states.states import AddConference
from bot.core.keyboards import back_button, ocr_buttons, data_buttons, hashtags_keyboard
from bot.core.constants import MESSAGES
from bot.core.callbacks import AdminCallback, FlowCallback
from bot.services import AdminService,ConferenceService


router = Router()


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
    await state.set_state(AddConference.ocr_check)
    await message.answer(
        MESSAGES["add-conf"]["ocr-stub"],
        reply_markup=ocr_buttons()
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
    await state.set_state(AddConference.hashtags)
    await callback.message.edit_text(
        MESSAGES["add-conf"]["add-tags"],
        reply_markup=hashtags_keyboard(tags, [])
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
