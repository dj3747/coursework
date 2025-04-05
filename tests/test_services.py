from datetime import datetime

# Тестируемые функции
from src.services import (analyze_cashback_categories,
                          calculate_cashback_by_category,
                          filter_transactions_by_date,
                          parse_date)


def test_parse_date():
    # Корректные данные
    assert parse_date("15.12.2023") == datetime(2023, 12, 15)
    assert parse_date("01.01.2024 12:30:45") == datetime(2024, 1, 1, 12, 30, 45)

    # Некорректные данные
    assert parse_date("2023-12-15") is None
    assert parse_date("invalid_date") is None


def test_filter_transactions_by_date():
    transactions = [
        {"Дата операции": datetime(2023, 12, 15), "Сумма операции": -5000.0},
        {"Дата операции": datetime(2024, 1, 10), "Сумма операции": -3000.0},
        {"Дата операции": datetime(2023, 12, 20), "Сумма операции": 2000.0},
    ]

    result = filter_transactions_by_date(transactions, 2023, 12)
    assert len(result) == 1
    assert result[0]["Сумма операции"] == -5000.0


def test_calculate_cashback_by_category():
    transactions = [
        {"Категория": "Супермаркеты", "Сумма операции": -1000.0},
        {"Категория": "Супермаркеты", "Сумма операции": -2000.0},
        {"Категория": "Транспорт", "Сумма операции": -500.0},
    ]

    result = calculate_cashback_by_category(transactions)
    assert result == {"Супермаркеты": 30.0, "Транспорт": 5.0}


def test_analyze_cashback_categories():
    transactions = [
        {"Дата операции": "15.12.2023", "Категория": "Супермаркеты", "Сумма операции": -1000.0},
        {"Дата платежа": "20.12.2023", "Категория": "Транспорт", "Сумма операции": -500.0},
    ]

    result = analyze_cashback_categories(transactions, 2023, 12)
    assert result == {"Супермаркеты": 10.0, "Транспорт": 5.0}
