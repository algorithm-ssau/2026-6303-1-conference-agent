from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.core.keyboards.admin import hashtags_keyboard
from bot.core.states.states import AddConference
from bot.core.keyboards.common import back_button
from bot.core.keyboards.admin import ocr_buttons, data_buttons
from bot.core.constants import callbacks as cb
from .common import is_admin

router = Router()


@router.callback_query(F.data == cb.ADD_CONF)
async def add_conf(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return

    await state.set_state(AddConference.waiting_for_file)
    await callback.message.edit_text(
        "Пришлите файл", 
        reply_markup=back_button()
        )


@router.message(AddConference.waiting_for_file)
async def process_file(message: Message, state: FSMContext):
    await state.set_state(AddConference.ocr_check)
    await message.answer(
        "Заглушка OCR:\n\nТекст...", 
        reply_markup=ocr_buttons()
        )


@router.callback_query(F.data == cb.OCR_OK)
async def ocr_ok(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddConference.data_check)
    await callback.message.edit_text(
        "Название: ...\nДата: ...\nДедлайн: ...",
        reply_markup=data_buttons()
    )


@router.callback_query(F.data == cb.DATA_OK)
async def data_ok(callback: CallbackQuery, state: FSMContext):
    tags = ["#ai", "#ml", "#nlp", "#cv", "#robotics", "#python", "#science"]

    await state.update_data(
        available_tags=tags,
        selected_tags=[]
    )
    
    await state.set_state(AddConference.hashtags)
    
    await callback.message.edit_text(
        "Выберите хэштеги:",
        reply_markup=hashtags_keyboard(tags, [])
    )