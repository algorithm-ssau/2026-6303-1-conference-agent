from aiogram.filters.callback_data import CallbackData 

class TagCallback(CallbackData, prefix="tag"):
  action: str  # toggle | add | finish
  tag: str | None = None

class AdminCallback(CallbackData, prefix="admin"):
  action: str  # add_conf | add_admin
  
class FlowCallback(CallbackData, prefix="flow"):
  action: str  # ocr_ok | data_ok | publish  