# -*- coding: utf-8 -*-
"""
analytics.py
Реалізує аналітичні функції та алгоритм пріоритизації вимог
(п. 4.4 ТЗ "Аналіз та пріоритизація").

Підтримуються два методи, які реально використовуються в практиці
бізнес-аналітика:
  1. MoSCoW — категорійна пріоритизація (Must/Should/Could/Won't)
  2. Impact/Effort матриця — кількісне ранжування за співвідношенням
     "цінність для бізнесу" / "трудомісткість реалізації"
"""

from typing import List, Dict
from collections import Counter
from models import Requirement, MOSCOW, STATUSES, CATEGORIES


def group_counts(requirements: List[Requirement], attr: str) -> Dict[str, int]:
    """Універсальний підрахунок кількості вимог за значенням атрибута
    (наприклад, скільки вимог у кожному статусі чи категорії)."""
    return dict(Counter(getattr(r, attr) for r in requirements))


def prioritize_moscow(requirements: List[Requirement]) -> Dict[str, List[Requirement]]:
    """Групує вимоги за методом MoSCoW, усередині групи сортує
    за priority_score (вплив/зусилля) — від найвигідніших до найменш вигідних."""
    grouped = {p: [] for p in MOSCOW}
    for r in requirements:
        grouped[r.priority].append(r)
    for p in grouped:
        grouped[p].sort(key=lambda r: r.priority_score, reverse=True)
    return grouped


def impact_effort_matrix(requirements: List[Requirement]) -> Dict[str, List[Requirement]]:
    """Розподіляє вимоги по квадрантах класичної матриці Impact/Effort:
      - quick_wins: високий вплив, низькі зусилля (impact>=4, effort<=2) — робити першими
      - major_projects: високий вплив, високі зусилля (impact>=4, effort>=3) — планувати окремо
      - fill_ins: низький вплив, низькі зусилля (impact<=3, effort<=2) — робити, якщо є час
      - thankless: низький вплив, високі зусилля (impact<=3, effort>=3) — уникати/відкласти
    """
    quadrants = {"quick_wins": [], "major_projects": [], "fill_ins": [], "thankless": []}
    for r in requirements:
        high_impact = r.impact >= 4
        low_effort = r.effort <= 2
        if high_impact and low_effort:
            quadrants["quick_wins"].append(r)
        elif high_impact and not low_effort:
            quadrants["major_projects"].append(r)
        elif not high_impact and low_effort:
            quadrants["fill_ins"].append(r)
        else:
            quadrants["thankless"].append(r)
    return quadrants


def summary_report(requirements: List[Requirement]) -> Dict:
    """Формує загальний аналітичний звіт: розподіли за категоріями,
    пріоритетами, статусами та середній priority_score."""
    if not requirements:
        return {
            "total": 0, "by_category": {}, "by_priority": {},
            "by_status": {}, "avg_priority_score": 0.0,
        }

    avg_score = round(sum(r.priority_score for r in requirements) / len(requirements), 2)
    return {
        "total": len(requirements),
        "by_category": group_counts(requirements, "category"),
        "by_priority": group_counts(requirements, "priority"),
        "by_status": group_counts(requirements, "status"),
        "avg_priority_score": avg_score,
    }


def render_bar_chart(counts: Dict[str, int], width: int = 30) -> str:
    """Будує просту текстову (ASCII) гістограму для консольної візуалізації
    розподілу вимог — заміна графічного UI для навчального консольного проєкту."""
    if not counts:
        return "(немає даних)"
    max_count = max(counts.values()) or 1
    lines = []
    for label, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        bar_len = int((count / max_count) * width)
        bar = "█" * bar_len
        lines.append(f"  {label:<20} {bar} {count}")
    return "\n".join(lines)
