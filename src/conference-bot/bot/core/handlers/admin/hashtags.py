from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from bot.core.constants import callbacks as cb
from bot.core.states.states import AddConference
from bot.core.keyboards.admin import hashtags_keyboard, post_buttons
from bot.core.keyboards.common import back_button

router = Router()


@router.callback_query(F.data.startswith(cb.TOGGLE_TAG))
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


@router.callback_query(F.data == cb.ADD_TAG)
async def add_tag(callback: CallbackQuery, state: FSMContext):
    # Устанавливаем состояние для ожидания нового тега
    await state.set_state(AddConference.hashtags)
    await callback.message.edit_text(
        "Введите новый хэштег:", 
        reply_markup=back_button()
    )


# ???????????
@router.callback_query(F.data == cb.FINISH_TAGS)
async def finish_tags(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get("selected_tags", [])
    
    # Здесь должна быть логика перехода к следующему шагу
    # Например, показ предварительного просмотра поста
    await callback.message.edit_text(
        f"Вы выбрали теги: {' '.join(selected)}\n\nПереход к следующему шагу...",
        reply_markup=post_buttons()  # Добавьте нужную клавиатуру
    )
    # Устанавливаем следующее состояние
    await state.set_state(AddConference.post)


@router.message(AddConference.hashtags)
async def process_new_tag(message: Message, state: FSMContext):
    new_tag = message.text.strip()

    if not new_tag.startswith("#"):
        new_tag = "#" + new_tag

    data = await state.get_data()
    tags = data.get("available_tags", [])
    selected = data.get("selected_tags", [])

    if new_tag not in tags:
        tags.append(new_tag)

    if new_tag not in selected:
        selected.append(new_tag)

    await state.update_data(
        available_tags=tags,
        selected_tags=selected
    )

    # Возвращаемся к клавиатуре с тегами
    await message.answer(
        f"Тег {new_tag} добавлен. Выберите теги:",
        reply_markup=hashtags_keyboard(tags, selected)
    )