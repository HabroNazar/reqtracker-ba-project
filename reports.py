# -*- coding: utf-8 -*-
"""
reports.py
Реалізує експорт вимог у форматах CSV та текстового звіту
(п. 4.5 ТЗ "Звітність та експорт даних"). CSV дозволяє подальшу обробку
в Excel/Power BI — типовий сценарій роботи бізнес-аналітика.
"""

import csv
from typing import List
from models import Requirement
from analytics import summary_report, prioritize_moscow, impact_effort_matrix, render_bar_chart


def export_csv(requirements: List[Requirement], filepath: str) -> None:
    """Експортує повний список вимог у CSV-файл (UTF-8 з BOM для коректного
    відкриття кирилиці в Excel)."""
    fieldnames = ["id", "title", "description", "stakeholder", "category",
                  "priority", "impact", "effort", "priority_score", "status", "created_at"]
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in requirements:
            writer.writerow(r.to_dict())


def generate_text_report(requirements: List[Requirement]) -> str:
    """Формує комплексний текстовий звіт: загальна статистика, розподіли,
    MoSCoW-групування та Impact/Effort матриця. Використовується як вивід
    в консоль і як вміст текстового файлу-звіту."""
    lines = []
    lines.append("=" * 70)
    lines.append("ЗВІТ З АНАЛІЗУ ТА ПРІОРИТИЗАЦІЇ БІЗНЕС-ВИМОГ")
    lines.append("=" * 70)

    summary = summary_report(requirements)
    lines.append(f"\nЗагальна кількість вимог: {summary['total']}")
    lines.append(f"Середній priority_score (impact/effort): {summary['avg_priority_score']}")

    lines.append("\n--- Розподіл за категоріями ---")
    lines.append(render_bar_chart(summary["by_category"]))

    lines.append("\n--- Розподіл за статусами ---")
    lines.append(render_bar_chart(summary["by_status"]))

    lines.append("\n--- Розподіл за пріоритетом (MoSCoW) ---")
    lines.append(render_bar_chart(summary["by_priority"]))

    lines.append("\n" + "=" * 70)
    lines.append("ПРІОРИТИЗАЦІЯ ЗА МЕТОДОМ MoSCoW")
    lines.append("=" * 70)
    moscow_groups = prioritize_moscow(requirements)
    from models import MOSCOW_LABELS
    for key in ["must", "should", "could", "wont"]:
        items = moscow_groups[key]
        lines.append(f"\n{MOSCOW_LABELS[key]} — {len(items)} вимог(и)")
        for r in items:
            lines.append(f"  [#{r.id}] {r.title} (score={r.priority_score}, статус={r.status})")

    lines.append("\n" + "=" * 70)
    lines.append("МАТРИЦЯ IMPACT / EFFORT")
    lines.append("=" * 70)
    matrix = impact_effort_matrix(requirements)
    matrix_labels = {
        "quick_wins": "Quick Wins (високий вплив, мало зусиль) — робити першими",
        "major_projects": "Major Projects (високий вплив, багато зусиль) — планувати окремо",
        "fill_ins": "Fill-ins (низький вплив, мало зусиль) — за наявності часу",
        "thankless": "Thankless (низький вплив, багато зусиль) — уникати/відкласти",
    }
    for key, label in matrix_labels.items():
        items = matrix[key]
        lines.append(f"\n{label} — {len(items)} вимог(и)")
        for r in items:
            lines.append(f"  [#{r.id}] {r.title} (impact={r.impact}, effort={r.effort})")

    return "\n".join(lines)


def save_text_report(requirements: List[Requirement], filepath: str) -> None:
    """Зберігає текстовий звіт у файл."""
    text = generate_text_report(requirements)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)
