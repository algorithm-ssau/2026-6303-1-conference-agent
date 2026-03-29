'''
  ocr_buttons() - панель для коррекции сгенерированного поста
  data_buttons()
  hashtag_buttons() - панель для выбора и добавления хештегов к посту
  post_buttons() - панель для публикации в тгк / сохранения сгенерированного и прошедшего проверку поста
'''

from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.core.constants import callbacks as cb


def ocr_buttons():
  kb = InlineKeyboardBuilder()
  kb.button(text="✅ Всё верно", callback_data=cb.OCR_OK)
  kb.button(text="✏️ Исправить", callback_data=cb.OCR_EDIT)
  kb.button(text="❌ Отмена", callback_data=cb.MAIN_MENU)
  kb.adjust(1)
  return kb.as_markup()


def data_buttons():
  kb = InlineKeyboardBuilder()
  kb.button(text="✅ Сохранить", callback_data=cb.DATA_OK)
  kb.button(text="🔄 Перегенерировать", callback_data=cb.DATA_REGEN)
  kb.button(text="❌ Отмена", callback_data=cb.MAIN_MENU)
  kb.adjust(1)
  return kb.as_markup()



def hashtags_keyboard(tags: list[str], selected: list[str]):
    kb = InlineKeyboardBuilder()

    for tag in tags:
      mark = "☑" if tag in selected else "☐"
      kb.button(
        text=f"{mark} {tag}",
        callback_data=f"{cb.TOGGLE_TAG}:{tag}"
      )

    kb.button(text="➕ Добавить свой", callback_data=cb.ADD_TAG)
    kb.button(text="✅ Готово", callback_data=cb.FINISH_TAGS)
    kb.button(text="❌ Отмена", callback_data=cb.MAIN_MENU)

    kb.adjust(1)
    return kb.as_markup()


def post_buttons():
  kb = InlineKeyboardBuilder()
  kb.button(text="📢 Опубликовать", callback_data=cb.PUBLISH)
  kb.button(text="💾 Сохранить", callback_data=cb.SAVE)
  kb.button(text="❌ Отмена", callback_data=cb.MAIN_MENU)
  kb.adjust(1)
  return kb.as_markup()