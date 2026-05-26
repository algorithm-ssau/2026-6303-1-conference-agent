from aiogram.fsm.state import State, StatesGroup

class AddConference(StatesGroup):
  waiting_for_file = State()
  text_check = State() # после OCR
  waiting_for_text_edit = State()  # ручное редактирование
  data_check = State() 
  post_check = State() # подтверждение текста поста
  hashtags = State()
  preview = State() # финальный просмотр

  
class AddAdmin(StatesGroup):
  waiting_user_name = State()
  add_new_admin = State()

class Search(StatesGroup):
  waiting_query = State()