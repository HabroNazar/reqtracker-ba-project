# -*- coding: utf-8 -*-
"""
repository.py
Реалізує сховище вимог (in-memory repository) та CRUD-операції
(п. 4.3 ТЗ "Управління даними"). Відокремлення сховища від бізнес-логіки
(repository pattern) дозволяє в майбутньому замінити in-memory список
на реальну БД без зміни решти системи.
"""

from typing import List, Optional, Dict
from models import Requirement


class RequirementRepository:
    """Сховище бізнес-вимог з автогенерацією ID та базовими CRUD-операціями."""

    def __init__(self):
        self._items: Dict[int, Requirement] = {}
        self._next_id = 1

    def add(self, req: Requirement) -> Requirement:
        """Додає нову вимогу, призначаючи унікальний ID автоматично."""
        req.id = self._next_id
        self._items[req.id] = req
        self._next_id += 1
        return req

    def get(self, req_id: int) -> Optional[Requirement]:
        return self._items.get(req_id)

    def update_status(self, req_id: int, status: str) -> bool:
        req = self.get(req_id)
        if not req:
            return False
        req.status = status
        return True

    def delete(self, req_id: int) -> bool:
        return self._items.pop(req_id, None) is not None

    def all(self) -> List[Requirement]:
        return list(self._items.values())

    def filter_by(self, category: str = None, priority: str = None,
                   status: str = None, stakeholder: str = None) -> List[Requirement]:
        """Універсальний фільтр за будь-якою комбінацією атрибутів."""
        result = self.all()
        if category:
            result = [r for r in result if r.category == category]
        if priority:
            result = [r for r in result if r.priority == priority]
        if status:
            result = [r for r in result if r.status == status]
        if stakeholder:
            result = [r for r in result if stakeholder.lower() in r.stakeholder.lower()]
        return result

    def count(self) -> int:
        return len(self._items)
