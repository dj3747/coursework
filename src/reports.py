import json
import logging
import os.path
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Optional

import pandas as pd

# Настройка логирования
logging.basicConfig(level=logging.INFO)


# Декоратор для записи отчета в файл
def log_report_to_file(filename: Optional[str] = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            nonlocal filename
            #  Если имя не передано, используем текущее время для имени файла
            if filename is None:
                filename = os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__),
                        "..",
                        "data",
                        f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    )
                )
            else:
                filename = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", filename.lstrip("../")))

            # Создаем директории если их нет
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            # Записываем результат в файл
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            logging.info(f"Отчет записан в файл: {filename}")
            return result

        return wrapper

    return decorator


@log_report_to_file("../data/spending_by_category_report.json")  # Можно передать имя файла
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> dict:
    """Функция для получения трат по категориям за заданный период"""
    # Создаем копию DataFrame для безопасной модификации
    df = transactions.copy()

    # Определение целевой даты
    target_date = datetime.now() if date is None else datetime.strptime(date, "%Y-%m-%d")

    # Преобразование дат в DataFrame
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True, errors="coerce")

    # Вычисляем дату 3 месяца назад
    start_date = target_date - timedelta(days=90)

    # Фильтруем транзакции по категории и дате
    mask = (df["Категория"] == category) & (df["Дата операции"] >= start_date)
    filtered_transactions = df.loc[mask].copy()

    # Возвращаем сумму трат по категориям
    total_spending = float(filtered_transactions["Сумма операции"].sum())

    # Преобразуем столбец 'Дата операции' в строку для JSON
    filtered_transactions["Дата операции"] = filtered_transactions["Дата операции"].dt.strftime("%Y-%m-%d %H:%M:%S")

    return {
        "category": category,
        "total_spending": total_spending,
        "transactions": filtered_transactions[["Дата операции", "Сумма операции", "Описание"]].to_dict(
            orient="records"
        ),
    }


# Пример использования
if __name__ == "__main__":
    # Загружаем данные из Excel файла
    df = pd.read_excel(os.path.join(os.path.dirname(__file__), "..", "data", "operations.xlsx"))

    # Пример вызова функции с категорией и датой
    result = spending_by_category(transactions=df, category="Супермаркеты", date="2020-05-20")
    print(result)
