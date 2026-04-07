# bot/repositories/conference_repository.py

from bot.repositories.db_manager import add_conference, search_conferences

class ConferenceRepository:

  @staticmethod
  async def create(data: dict) -> int:
    return add_conference(
      name=data.get("name"),
      conference_date=data.get("conference_date"),
      location=data.get("location"),
      submission_deadline=data.get("submission_deadline")
    )

  @staticmethod
  async def search(query: str):
    return search_conferences(query)