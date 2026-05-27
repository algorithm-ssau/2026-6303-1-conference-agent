from aiogram.fsm.state import State, StatesGroup

class AddConference(StatesGroup):
  waiting_for_file = State()
  text_check = State() # после OCR
  waiting_for_text_edit = State()  # ручное редактирование
  data_check = State() 
  waiting_for_data_edit = State() # ручное редактирование отпарсенных данных
  post_check = State() # подтверждение текста поста
  waiting_for_post_edit = State() # ручное редактирование поста
  hashtags = State()
  preview = State() # финальный просмотр

  
class AddAdmin(StatesGroup):
  waiting_user_name = State()
  add_new_admin = State()

class Search(StatesGroup):
  waiting_query = State()