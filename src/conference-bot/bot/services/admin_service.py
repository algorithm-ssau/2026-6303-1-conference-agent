from typing import Dict, Any, List
from bot.config import ADMIN_IDS
from bot.core.constants import MESSAGES
from bot.database import AdminRepository
import re

class AdminService:
  """
    Сервис для управления администраторами
  """
  
  @staticmethod
  def is_admin(user_id: int, username: str | None = None) -> bool:
    if user_id in ADMIN_IDS:
      return True

    if username:
      return AdminRepository.is_admin(username.lower())

    return False
  
  
  @staticmethod
  async def add_admin(username: str, added_by: int) -> Dict[str, Any]:
    """
      Добавляет нового администратора
    """
    if added_by not in ADMIN_IDS:
      raise PermissionError("Нет прав")

    success = AdminRepository.add_admin(username, added_by)

    if not success:
      return {
        "success": False,
        "reason": "already_exists"
      }
    
    return {
      "success": True,
      "username": username,
      "message": f"Пользователь {username} добавлен в список администраторов"
    }
  
  
  @staticmethod
  def get_admins() -> List[str]:
    """
      Возвращает список ID администраторов
    """
    return AdminRepository.get_all()
  
  
  @staticmethod
  def validate_username(username: str) -> bool:
    """
      Валидирует username
    """
    if not username:
      return False
    
    if username.startswith("@"):
      username = username[1:]
        
    if len(username) < 5 or len(username) > 32:
      return False
        
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_]+$', username):
      return False
      
    return len(username) >= 3