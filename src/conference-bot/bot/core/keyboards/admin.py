from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.core.callbacks import TagCallback, FlowCallback
from bot.core.constants import callbacks as cb


def ocr_buttons():
  kb = InlineKeyboardBuilder()
  kb.button(
    text="✅ Всё верно", 
    callback_data=FlowCallback(action="ocr_ok").pack()
  )
  kb.button(
    text="✏️ Исправить (в разработке)", 
    callback_data=cb.DISABLED
    # callback_data=cb.OCR_EDIT
  )
  kb.button(
    text="❌ Отмена", 
    callback_data=cb.MAIN_MENU
  )
  kb.adjust(1)
  return kb.as_markup()


def data_buttons():
  kb = InlineKeyboardBuilder()
  kb.button(
    text="✅ Сохранить", 
    callback_data=FlowCallback(action="data_ok").pack()
  )
  kb.button(
    text="✏️ Исправить (в разработке)", 
    callback_data=cb.DISABLED
    # callback_data=cb.DATA_REGEN
  )
  kb.button(
    text="❌ Отмена", 
    callback_data=cb.MAIN_MENU
    )
  kb.adjust(1)
  return kb.as_markup()



def hashtags_keyboard(tags: list[str], selected: list[str]):
    kb = InlineKeyboardBuilder()

    for tag in tags:
      mark = "☑" if tag in selected else "☐"
      kb.button(
        text=f"{mark} {tag}",
        callback_data=TagCallback(action="toggle", tag=tag).pack()
      )

    kb.button(
      text="➕ Добавить свой", 
      callback_data=TagCallback(action="add").pack()
    )
    kb.button(
      text="✅ Готово", 
      callback_data=TagCallback(action="finish").pack()
      )
    kb.button(
      text="❌ Отмена", 
      callback_data=cb.MAIN_MENU
    )

    kb.adjust(1)
    return kb.as_markup()


def post_buttons():
  kb = InlineKeyboardBuilder()
  kb.button(
    text="📢 Опубликовать", 
    callback_data=FlowCallback(action="publish").pack()
  )
  kb.button(
    text="💾 Сохранить (в разработке)", 
    callback_data=cb.DISABLED
    # callback_data=cb.SAVE
  )
  kb.button(
    text="❌ Отмена", 
    callback_data=cb.MAIN_MENU
  )
  kb.adjust(1)
  return kb.as_markup()


def confirmation_buttons():
  kb = InlineKeyboardBuilder()
  kb.button(text="✅ Да, добавить", callback_data=cb.CONFIRM_ADD_ADMIN)
  kb.button(text="❌ Отмена", callback_data=cb.MAIN_MENU)
  kb.adjust(1)
  return kb.as_markup()