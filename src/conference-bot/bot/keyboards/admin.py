from aiogram.utils.keyboard import InlineKeyboardBuilder



'''
  ocr_buttons() - панель для коррекции сгенерированного поста
  
  data_buttons()
  
  hashtag_buttons() - панель для выбора и добавления хештегов к посту
  
  post_buttons() - панель для публикации в тгк / сохранения 
                   сгенерированного и прошедшего проверку поста
'''

def ocr_buttons():
  kb = InlineKeyboardBuilder()
  kb.button(text="✅ Всё верно", callback_data="ocr_ok")
  kb.button(text="✏️ Исправить", callback_data="ocr_edit")
  kb.button(text="❌ Отмена", callback_data="main_menu")
  kb.adjust(1)
  return kb.as_markup()


def data_buttons():
  kb = InlineKeyboardBuilder()
  kb.button(text="✅ Сохранить", callback_data="data_ok")
  kb.button(text="🔄 Перегенерировать", callback_data="data_regen")
  kb.button(text="❌ Отмена", callback_data="main_menu")
  kb.adjust(1)
  return kb.as_markup()


def hashtag_buttons():
  kb = InlineKeyboardBuilder()
  kb.button(text="➕ Добавить свой", callback_data="add_tag")
  kb.button(text="➡ Далее", callback_data="to_post")
  kb.button(text="❌ Отмена", callback_data="main_menu")
  kb.adjust(1)
  return kb.as_markup()


def post_buttons():
  kb = InlineKeyboardBuilder()
  kb.button(text="📢 Опубликовать", callback_data="publish")
  kb.button(text="💾 Сохранить", callback_data="save")
  kb.button(text="❌ Отмена", callback_data="main_menu")
  kb.adjust(1)
  return kb.as_markup()