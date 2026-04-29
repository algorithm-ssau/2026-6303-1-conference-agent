from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.core.constants import callbacks as cb

def search_buttons(has_more: bool = False, offset: int = 0):
  """
    Создает клавиатуру для результатов поиска
    
    Args:
      has_more: Есть ли еще результаты для показа (если результов 5 <)
      offset: Текущее смещение (нужно для кнопки "Показать ещё")
  """
  kb = InlineKeyboardBuilder()
  
  if has_more:
    kb.button(
      text="➡ Показать ещё", 
      callback_data=f"{cb.MORE}:{offset}"
    )
  
  kb.button(text="🔍 Новый поиск", callback_data=cb.SEARCH)
  kb.button(text="⬅ Меню", callback_data=cb.MAIN_MENU)
  kb.adjust(1)
  return kb.as_markup()

def search_buttons_simple():
  kb = InlineKeyboardBuilder()
  kb.button(text="🔍 Новый поиск", callback_data=cb.SEARCH)
  kb.button(text="⬅ Меню", callback_data=cb.MAIN_MENU)
  kb.adjust(1)
  return kb.as_markup()