from aiogram.fsm.state import State, StatesGroup

class AddConference(StatesGroup):
  waiting_for_file = State()
  ocr_check = State()
  data_check = State()
  hashtags = State()
  post = State()
  
class AddAdmin(StatesGroup):
  waiting_user_name = State()
  add_new_admin = State()

class Search(StatesGroup):
  waiting_query = State()