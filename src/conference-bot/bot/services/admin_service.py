from typing import Dict, Any, List
from bot.config import ADMIN_IDS
from bot.core.constants import MESSAGES

class AdminService:
  """
  Сервис для управления администраторами
  """
  
  @staticmethod
  def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS
  
  @staticmethod
  async def add_admin(username: str, added_by: int) -> Dict[str, Any]:
    """
    Добавляет нового администратора
    В будущем здесь будет логика добавления в БД
    """
    if not AdminService.is_admin(added_by):
      raise PermissionError(MESSAGES["errors"]["for-admin-only"])
    
    return {
      "success": True,
      "username": username,
      "message": f"Пользователь {username} добавлен в список администраторов"
    }
  
  @staticmethod
  def get_admins() -> List[int]:
    """
    Возвращает список ID администраторов
    """
    return ADMIN_IDS.copy()
  
  @staticmethod
  def validate_username(username: str) -> bool:
    """
    Валидирует username
    """
    
    if not username:
      return False
    if username.startswith("@"):
      username = username[1:]
      
    return username.isalnum() and len(username) >= 3