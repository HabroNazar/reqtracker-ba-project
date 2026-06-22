# -*- coding: utf-8 -*-
"""
models.py
Модель даних "Бізнес-вимога" (Business Requirement) та довідники.
Відповідає п. 4.2 ТЗ "Структура даних".

У реальній системі дані зберігалися б у БД (SQLite/PostgreSQL) або
надходили з зовнішніх систем (Jira, Confluence) через API. Для навчального
проєкту використовується in-memory структура з можливістю серіалізації
у CSV/JSON (модуль reports.py), що дозволяє повноцінно продемонструвати
весь життєвий цикл вимоги.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional

# --- Довідники (контрольовані словники) ---

CATEGORIES = [
    "функціональна",
    "нефункціональна",
    "бізнес-правило",
    "інтерфейсна",
    "технічна",
]

# Метод пріоритизації MoSCoW (стандарт BABOK / Agile BA practice)
MOSCOW = ["must", "should", "could", "wont"]

MOSCOW_LABELS = {
    "must": "Must have (обов'язково)",
    "should": "Should have (бажано)",
    "could": "Could have (можливо)",
    "wont": "Won't have (не зараз)",
}

STATUSES = ["новий", "на_аналізі", "узгоджено", "у_розробці", "виконано", "відхилено"]


@dataclass
class Requirement:
    """Бізнес-вимога — основна сутність системи.

    Поля відповідають класичній структурі картки вимоги в BA-практиці:
    ідентифікатор, назва, опис, джерело (стейкхолдер), категорія,
    пріоритет (MoSCoW), оцінки впливу/зусиль для матриці пріоритизації,
    статус та дата створення.
    """

    id: int
    title: str
    description: str
    stakeholder: str
    category: str = "функціональна"
    priority: str = "should"
    impact: int = 3        # 1-5: наскільки вимога критична для бізнесу
    effort: int = 3        # 1-5: оцінка трудомісткості реалізації
    status: str = "новий"
    created_at: date = field(default_factory=date.today)

    def __post_init__(self):
        if self.category not in CATEGORIES:
            raise ValueError(f"Невідома категорія: {self.category}")
        if self.priority not in MOSCOW:
            raise ValueError(f"Невідомий пріоритет: {self.priority}")
        if self.status not in STATUSES:
            raise ValueError(f"Невідомий статус: {self.status}")
        if not (1 <= self.impact <= 5) or not (1 <= self.effort <= 5):
            raise ValueError("impact та effort повинні бути в діапазоні 1-5")

    @property
    def priority_score(self) -> float:
        """Розрахунковий пріоритетний бал на основі співвідношення
        вплив/зусилля (RICE-подібний підхід, спрощений для навчальних цілей).
        Чим вищий impact і нижчий effort — тим вищий пріоритет."""
        return round(self.impact / self.effort, 2)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "stakeholder": self.stakeholder,
            "category": self.category,
            "priority": self.priority,
            "impact": self.impact,
            "effort": self.effort,
            "priority_score": self.priority_score,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }
