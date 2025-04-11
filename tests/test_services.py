import json
import logging
from datetime import datetime

import pytest
from openpyxl import Workbook

# Тестируемые функции
from src.services import (analyze_cashback_categories,
                          calculate_cashback_by_category,
                          filter_transactions_by_date,
                          load_data_from_excel,
                          parse_date,
                          save_result_to_file)


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


def test_load_data_from_excel_file_not_found():
    """Тест, когда файл Excel не найден (вызывает исключение FileNotFoundError)."""
    with pytest.raises(FileNotFoundError):
        load_data_from_excel("non_existent_file.xlsx")


def test_load_data_from_excel_empty_file(tmp_path):
    """Тест с пустым Excel файлом."""
    file_path = tmp_path / "test_data.xlsx"
    workbook = Workbook()
    workbook.save(file_path)
    loaded_data = load_data_from_excel(str(file_path))
    assert loaded_data == []


def test_save_result_to_file_invalid_file_path(tmp_path, caplog):
    """Тест с некорректным путем к файлу (ошибка создания директории)."""
    caplog.set_level(logging.ERROR)
    test_result = {"value": 123}
    file_path = tmp_path / "non_existent_dir" / "test_result.json"  # Директория не существует

    with pytest.raises(FileNotFoundError):
        save_result_to_file(test_result, str(file_path))


def test_save_result_to_file_non_ascii_data(tmp_path, caplog):
    """Тест с данными, содержащими не-ASCII символы."""
    caplog.set_level(logging.INFO)
    test_result = {"name": "Иван", "city": "Москва"}  # Данные с кириллицей
    file_path = tmp_path / "test_result.json"

    save_result_to_file(test_result, str(file_path))

    # Проверяем, что файл был создан и содержит ожидаемые данные (с кириллицей)
    with open(file_path, "r", encoding="utf-8") as file:
        loaded_result = json.load(file)
    assert loaded_result == test_result

    # Проверяем сообщение в логе
    assert f"Результаты сохранены в файл {file_path}" in caplog.text
