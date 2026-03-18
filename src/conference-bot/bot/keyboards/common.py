from aiogram.utils.keyboard import InlineKeyboardBuilder


'''
  main_menu(is_admin) - главная панель бота, имеет два варианта отображения 
    (с кнопкой "добавить конференцию" / без) в зависимости от значения флага is_admin
  
  back_button() - кнопка, возвращающая в главную панель
'''



def main_menu(is_admin=False):
  kb = InlineKeyboardBuilder()
  kb.button(text="🔎 Найти конференции", callback_data="search")
  kb.button(text="ℹ️ О проекте", callback_data="about")

  if is_admin:
    kb.button(text="➕ Добавить конференцию", callback_data="add_conf")

  kb.adjust(1)
  return kb.as_markup()


def back_button():
  kb = InlineKeyboardBuilder()
  kb.button(text="⬅ Назад", callback_data="main_menu")
  return kb.as_markup()