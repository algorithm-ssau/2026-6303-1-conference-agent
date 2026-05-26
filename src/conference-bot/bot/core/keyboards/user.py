from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.core.constants import callbacks as cb

def search_buttons_simple():
  kb = InlineKeyboardBuilder()
  kb.button(text="🔍 Новый поиск", callback_data=cb.SEARCH)
  kb.button(text="⬅ Меню", callback_data=cb.MAIN_MENU)
  kb.adjust(1)
  return kb.as_markup()