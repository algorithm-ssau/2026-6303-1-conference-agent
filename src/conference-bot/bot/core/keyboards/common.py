from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.core.constants import callbacks as cb
from bot.core.callbacks import AdminCallback

def main_menu(is_admin=False):
  kb = InlineKeyboardBuilder()
  kb.button(text="🔎 Найти конференции", callback_data=cb.SEARCH)
  kb.button(text="ℹ️ О проекте", callback_data=cb.ABOUT)

  if is_admin:
    kb.button(
      text="➕ Добавить конференцию", 
      callback_data=AdminCallback(action="add_conf").pack()
    )
    kb.button(
      text="➕ Добавить админа", 
      callback_data=AdminCallback(action="add_admin").pack()
      )

  kb.adjust(1)
  return kb.as_markup()


def back_button():
  kb = InlineKeyboardBuilder()
  kb.button(text="⬅ Назад", callback_data=cb.MAIN_MENU)
  return kb.as_markup()