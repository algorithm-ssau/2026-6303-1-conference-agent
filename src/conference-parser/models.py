from pydantic import BaseModel, Field
from typing import Optional, List


class DeadlineInfo(BaseModel):
    date: str = Field(description="Сама дата (например: 10.12.2025)")
    description: str = Field(description="Краткое пояснение, что это за дата (например: Прием заявок)")


class LinkInfo(BaseModel):
    url: str = Field(description="Полный URL-адрес")
    description: str = Field(description="Пояснение, куда ведет ссылка (например: Регистрация, Сайт)")


class EventData(BaseModel):
    event_name: Optional[str] = Field(description="Название мероприятия")
    event_type: Optional[str] = Field(description="Тип (конференция, школа, конкурс)")
    organizer: Optional[str] = Field(description="Организация (организатор)")
    dates: Optional[str] = Field(description="Даты или период проведения мероприятия")
    status: Optional[str] = Field(description="Статус (Международная, Всероссийская и т.д.)")

    deadlines: Optional[List[DeadlineInfo]] = Field(description="Список важных дат с описаниями")
    links: Optional[List[LinkInfo]] = Field(description="Список ссылок с описаниями")

    topics: Optional[List[str]] = Field(description="Список научных направлений, секций или тематик мероприятия")
    location: Optional[str] = Field(description="Место проведения")
    rsci: Optional[bool] = Field(description="РИНЦ (true/false)")
    format: Optional[str] = Field(description="Офлайн / Онлайн / Гибридный")
    target_audience: Optional[str] = Field(description="Целевая аудитория (студенты и т.д.)")
