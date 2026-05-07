from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.core.constants import callbacks as cb
from bot.core.keyboards import main_menu
from bot.services import AdminService

router = Router()

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