from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.core.constants import callbacks as cb

'''
  main_menu(is_admin) - главная панель бота, имеет два варианта отображения 
    (с кнопкой "добавить конференцию" / без) в зависимости от значения флага is_admin
  
  back_button() - кнопка, возвращающая в главную панель
'''



def main_menu(is_admin=False):
  kb = InlineKeyboardBuilder()
  kb.button(text="🔎 Найти конференции", callback_data=cb.SEARCH)
  kb.button(text="ℹ️ О проекте", callback_data=cb.ABOUT)

  if is_admin:
    kb.button(text="➕ Добавить конференцию", callback_data=cb.ADD_CONF)
    kb.button(text="➕ Добавить админа", callback_data=cb.ADD_ADMIN)

  kb.adjust(1)
  return kb.as_markup()


def back_button():
  kb = InlineKeyboardBuilder()
  kb.button(text="⬅ Назад", callback_data=cb.MAIN_MENU)
  return kb.as_markup()