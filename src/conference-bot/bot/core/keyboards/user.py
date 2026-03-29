from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.core.constants import callbacks as cb

'''
  search_buttons() - панель кнопок для навигации по полученному списку конференций
    и навигации на другие панели
    - "Показать ещё" - следующие 5 конференций из поиска
    - "Новый поиск" - возвращение в панель поиска
'''


def search_buttons():
  kb = InlineKeyboardBuilder()
  kb.button(text="➡ Показать ещё", callback_data=cb.MORE)
  kb.button(text="🔍 Новый поиск", callback_data=cb.SEARCH)
  kb.button(text="⬅ Меню", callback_data=cb.MAIN_MENU)
  kb.adjust(1)
  return kb.as_markup()