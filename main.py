# -*- coding: utf-8 -*-
"""
main.py
Головний модуль інформаційної системи "ReqTracker" — системи аналізу
та візуалізації бізнес-вимог для бізнес-аналітика.

Реалізує консольне меню (п. 4.6 ТЗ "Інтерфейс користувача"), що зв'язує
модулі models, repository, analytics, reports у єдиний робочий сценарій:
  - реєстрація вимог від стейкхолдерів
  - перегляд та фільтрація
  - пріоритизація (MoSCoW, Impact/Effort)
  - формування аналітичних звітів та експорт у CSV/TXT

Запуск: python main.py
"""

from models import Requirement, CATEGORIES, MOSCOW, MOSCOW_LABELS, STATUSES
from repository import RequirementRepository
from analytics import summary_report, render_bar_chart
from reports import export_csv, generate_text_report, save_text_report

SEPARATOR = "-" * 70


def print_header():
    print(SEPARATOR)
    print("ReqTracker — система аналізу та візуалізації бізнес-вимог")
    print(SEPARATOR)


def seed_demo_data(repo: RequirementRepository) -> None:
    """Завантажує демонстраційний набір вимог, типовий для проєкту
    впровадження CRM-системи в компанії, щоб одразу показати роботу
    аналітики без ручного введення (корисно для демонстрації звіту)."""
    demo = [
        Requirement(id=0, title="Авторизація через корпоративний SSO",
                    description="Користувачі повинні входити в систему через єдиний вхід (SSO) компанії.",
                    stakeholder="ІТ-директор", category="нефункціональна",
                    priority="must", impact=5, effort=3, status="узгоджено"),
        Requirement(id=0, title="Форма реєстрації нового лідa",
                    description="Менеджер з продажу повинен мати можливість швидко створити картку нового ліда.",
                    stakeholder="Керівник відділу продажів", category="функціональна",
                    priority="must", impact=5, effort=2, status="у_розробці"),
        Requirement(id=0, title="Експорт звітів у Excel",
                    description="Можливість експортувати будь-який звіт по угодах у формат Excel.",
                    stakeholder="Фінансовий аналітик", category="функціональна",
                    priority="should", impact=3, effort=2, status="на_аналізі"),
        Requirement(id=0, title="Сповіщення про прострочені задачі",
                    description="Система повинна надсилати email, якщо задача по угоді просрочена більше 2 днів.",
                    stakeholder="Керівник відділу продажів", category="функціональна",
                    priority="should", impact=4, effort=2, status="новий"),
        Requirement(id=0, title="Інтеграція з телефонією (CTI)",
                    description="Автоматичне створення картки дзвінка при вхідному виклику клієнта.",
                    stakeholder="Керівник call-центру", category="інтерфейсна",
                    priority="could", impact=4, effort=5, status="новий"),
        Requirement(id=0, title="Темна тема інтерфейсу",
                    description="Можливість перемикання інтерфейсу системи в темний режим.",
                    stakeholder="Співробітники офісу", category="нефункціональна",
                    priority="wont", impact=1, effort=2, status="відхилено"),
        Requirement(id=0, title="Мультивалютність угод",
                    description="Підтримка ведення угод у кількох валютах з автоматичною конвертацією за курсом НБУ.",
                    stakeholder="Фінансовий директор", category="бізнес-правило",
                    priority="should", impact=4, effort=4, status="на_аналізі"),
        Requirement(id=0, title="Аудит дій користувачів",
                    description="Система повинна логувати всі критичні дії користувачів (зміна/видалення угод).",
                    stakeholder="Служба безпеки", category="нефункціональна",
                    priority="must", impact=5, effort=3, status="новий"),
        Requirement(id=0, title="Мобільний застосунок для менеджерів",
                    description="Менеджери з продажу повинні мати доступ до системи з мобільного телефону.",
                    stakeholder="Керівник відділу продажів", category="технічна",
                    priority="could", impact=3, effort=5, status="новий"),
        Requirement(id=0, title="Автоматичний розподіл лідів між менеджерами",
                    description="Нові ліди автоматично розподіляються між менеджерами за round-robin алгоритмом.",
                    stakeholder="Керівник відділу продажів", category="функціональна",
                    priority="must", impact=5, effort=3, status="узгоджено"),
    ]
    for r in demo:
        repo.add(r)


def input_requirement(repo: RequirementRepository) -> None:
    """Інтерактивне додавання нової вимоги через консоль із валідацією вводу."""
    print("\nДодавання нової вимоги.")
    title = input("Назва вимоги: ").strip()
    description = input("Опис вимоги: ").strip()
    stakeholder = input("Стейкхолдер (хто ініціював): ").strip()

    category = choose_from_list("Категорія:", CATEGORIES)
    priority = choose_from_list("Пріоритет (MoSCoW):", MOSCOW, labels=MOSCOW_LABELS)

    impact = read_int_in_range("Оцінка впливу на бізнес (1-5): ", 1, 5)
    effort = read_int_in_range("Оцінка трудомісткості (1-5): ", 1, 5)

    req = Requirement(id=0, title=title, description=description, stakeholder=stakeholder,
                       category=category, priority=priority, impact=impact, effort=effort)
    repo.add(req)
    print(f"Вимогу додано з ID #{req.id} (priority_score={req.priority_score}).")


def choose_from_list(prompt: str, options: list, labels: dict = None) -> str:
    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        display = labels[opt] if labels else opt
        print(f"  {i}. {display}")
    while True:
        raw = input("Ваш вибір (номер): ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print("Некоректний номер, спробуйте ще раз.")


def read_int_in_range(prompt: str, lo: int, hi: int) -> int:
    while True:
        raw = input(prompt).strip()
        if raw.isdigit() and lo <= int(raw) <= hi:
            return int(raw)
        print(f"Введіть число від {lo} до {hi}.")


def list_requirements(requirements) -> None:
    if not requirements:
        print("\nВимог не знайдено.")
        return
    print(f"\n{SEPARATOR}")
    for r in requirements:
        print(f"#{r.id:<3} [{r.priority.upper():<7}] [{r.status:<12}] {r.title}")
        print(f"      Категорія: {r.category} | Impact: {r.impact} | Effort: {r.effort} | "
              f"Score: {r.priority_score} | Стейкхолдер: {r.stakeholder}")
    print(SEPARATOR)


def main_menu():
    repo = RequirementRepository()
    seed_demo_data(repo)
    print(f"Завантажено демонстраційний набір: {repo.count()} вимог.\n")

    while True:
        print(f"\n{SEPARATOR}\nГоловне меню:")
        print("  1. Додати нову вимогу")
        print("  2. Показати всі вимоги")
        print("  3. Фільтрувати вимоги (за категорією/пріоритетом/статусом)")
        print("  4. Змінити статус вимоги")
        print("  5. Сформувати аналітичний звіт (консоль)")
        print("  6. Експортувати дані (CSV + TXT звіт у файли)")
        print("  7. Вийти")
        choice = input("Ваш вибір: ").strip()

        if choice == "1":
            input_requirement(repo)
        elif choice == "2":
            list_requirements(repo.all())
        elif choice == "3":
            print("\nЗалиште поле порожнім, щоб не фільтрувати за ним.")
            category = input(f"Категорія {CATEGORIES}: ").strip() or None
            priority = input(f"Пріоритет {MOSCOW}: ").strip() or None
            status = input(f"Статус {STATUSES}: ").strip() or None
            list_requirements(repo.filter_by(category=category, priority=priority, status=status))
        elif choice == "4":
            req_id = read_int_in_range("Введіть ID вимоги: ", 1, 9999)
            status = choose_from_list("Новий статус:", STATUSES)
            ok = repo.update_status(req_id, status)
            print("Статус оновлено." if ok else "Вимогу з таким ID не знайдено.")
        elif choice == "5":
            print("\n" + generate_text_report(repo.all()))
        elif choice == "6":
            export_csv(repo.all(), "requirements_export.csv")
            save_text_report(repo.all(), "requirements_report.txt")
            print("Дані експортовано у requirements_export.csv та requirements_report.txt")
        elif choice == "7":
            print("Роботу завершено. До побачення!")
            break
        else:
            print("Невідома команда, спробуйте ще раз.")


if __name__ == "__main__":
    print_header()
    main_menu()
