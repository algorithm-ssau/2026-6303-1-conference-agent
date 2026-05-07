from aiogram.fsm.state import State, StatesGroup

class AddConference(StatesGroup):
  waiting_for_file = State()
  text_check = State() # после OCR
  data_check = State() 
  post_check = State() # подтверждение текста поста
  hashtags = State()
  preview = State() # финальный просмотр
  # ocr_check = State()
  # confirm_save = State()
  # post = State()
  
class AddAdmin(StatesGroup):
  waiting_user_name = State()
  add_new_admin = State()

class Search(StatesGroup):
  waiting_query = State()