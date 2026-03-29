from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.core.constants import callbacks as cb
from bot.core.states.states import AddConference
from bot.core.keyboards.admin import post_buttons
from bot.core.keyboards.common import main_menu
from bot.core.constants.messages import MESSAGES

router = Router()


@router.callback_query(F.data == cb.FINISH_TAGS)
async def finish_tags(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get("selected_tags", [])

    post_text = MESSAGES["stub-post"]["text"]
    post_text = (
        "Финальный вариант поста с хэштегами:\n"
        + "<blockquote>" + post_text + "</blockquote>"
    )

    if selected:
        post_text += "\n\n" + " ".join(selected)

    await state.update_data(post_text=post_text)

    await callback.message.edit_text(
        post_text,
        reply_markup=post_buttons(),
        parse_mode="HTML"
    )

    await state.set_state(AddConference.post)


@router.callback_query(F.data == cb.PUBLISH)
async def publish(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Пост опубликован (заглушка).",
        reply_markup=main_menu(True)
    )