from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.core.states.states import AddAdmin
from bot.core.keyboards.common import back_button
from bot.core.keyboards.admin import ocr_buttons
from .common import is_admin

router = Router()

@router.callback_query(F.data == "add_admin")
async def add_admin(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return

    await state.set_state(AddAdmin.waiting_user_name)
    await callback.message.edit_text(
        "Введите @username:",
        reply_markup=back_button()
    )


@router.message(AddAdmin.waiting_user_name)
async def process_admin(message: Message, state: FSMContext):
    await state.set_state(AddAdmin.add_new_admin)
    await message.answer("Заглушка добавления админа", reply_markup=ocr_buttons())