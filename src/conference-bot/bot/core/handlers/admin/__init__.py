from aiogram import Router
from bot.core.handlers.admin import add_conference, hashtags, publish, add_admin, cancel_anywhere

def get_admin_router():
  router = Router()
  
  router.include_router(add_conference.router)
  router.include_router(hashtags.router)
  router.include_router(publish.router)
  router.include_router(add_admin.router)

  return router