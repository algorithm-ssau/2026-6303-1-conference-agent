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
    text="✏️ Исправить ", 
    callback_data=FlowCallback(action="ocr_edit").pack()
    # callback_data=cb.DISABLED
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
    text="✏️ Исправить", 
    callback_data=FlowCallback(action="data_edit").pack()
    # callback_data=cb.DISABLED
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

  for i, tag in enumerate(tags):
    mark = "☑" if tag in selected else "☐"
    kb.button(
      text=f"{mark} {tag}",
      callback_data=TagCallback(
        action="toggle",
        tag=str(i)   # ← ВАЖНО: индекс вместо текста
      ).pack()
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
    text="💾 Сохранить", 
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
  kb.button(
    text="✅ Да, добавить", 
    callback_data=cb.CONFIRM_ADD_ADMIN
    )
  kb.button(
    text="❌ Отмена", 
    callback_data=cb.MAIN_MENU
    )
  kb.adjust(1)
  return kb.as_markup()

def generate_post_buttons():
  kb = InlineKeyboardBuilder()
  kb.button(
      text="📝 Сгенерировать пост",
      callback_data=FlowCallback(action="generate_post").pack()
  )
  kb.button(
      text="⬅ В меню",
      callback_data=cb.MAIN_MENU
  )
  kb.adjust(1)
  return kb.as_markup()

def post_edit_buttons():
  kb = InlineKeyboardBuilder()
  kb.button(
    text="✏️ Редактировать",
    callback_data=FlowCallback(action="post_edit").pack()
    # callback_data=cb.DISABLED
  )
  kb.button(
    text="🔁 Перегенерировать",
    callback_data=FlowCallback(action="regen_post").pack()
    # callback_data=cb.DISABLED
  )
  kb.button(
    text="➡ К тегам",
    callback_data=FlowCallback(action="to_tags").pack()
  )
  kb.button(
    text="❌ Отмена",
    callback_data=cb.MAIN_MENU
  )
  kb.adjust(1)
  return kb.as_markup()

def confirm_conf_buttons():
  kb = InlineKeyboardBuilder()
  kb.button(text="✅ Сохранить", callback_data=cb.CONFIRM_SAVE_CONF)
  kb.button(text="❌ Отмена", callback_data=cb.MAIN_MENU)
  kb.adjust(1)
  return kb.as_markup()