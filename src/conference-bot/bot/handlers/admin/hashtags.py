from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.states.states import AddConference
from bot.keyboards.admin import hashtags_keyboard

router = Router()


@router.callback_query(F.data.startswith("toggle_tag"))
async def toggle_tag(callback: CallbackQuery, state: FSMContext):
    tag = callback.data.split(":")[1]

    data = await state.get_data()
    tags = data["available_tags"]
    selected = data["selected_tags"]

    if tag in selected:
        selected.remove(tag)
    else:
        selected.append(tag)

    await state.update_data(selected_tags=selected)

    await callback.message.edit_reply_markup(
        reply_markup=hashtags_keyboard(tags, selected)
    )


@router.callback_query(F.data == "add_tag")
async def add_tag(callback: CallbackQuery):
    await callback.message.answer("Введите новый хэштег:")


@router.message(AddConference.hashtags)
async def process_new_tag(message: Message, state: FSMContext):
    new_tag = message.text.strip()

    if not new_tag.startswith("#"):
        new_tag = "#" + new_tag

    data = await state.get_data()
    tags = data["available_tags"]
    selected = data["selected_tags"]

    if new_tag not in tags:
        tags.append(new_tag)

    if new_tag not in selected:
        selected.append(new_tag)

    await state.update_data(
        available_tags=tags,
        selected_tags=selected
    )

    await message.answer(
        "Тег добавлен.",
        reply_markup=hashtags_keyboard(tags, selected)
    )