import pandas as pd
import pytest

from src.reports import spending_by_category


@pytest.fixture
def sample_transactions():
    """Фикстура с тестовыми данными транзакций"""
    data = {
        "Дата операции": [
            "01.01.2021 12:00",
            "15.01.2021 09:30",
            "01.03.2021 18:15",
            "10.04.2021 14:00",
            "01.05.2021 10:00",
        ],
        "Категория": ["Супермаркеты", "Рестораны", "Супермаркеты", "Транспорт", "Супермаркеты"],
        "Сумма операции": [1500.0, 2500.0, 3000.0, 500.0, 2000.0],
        "Описание": ["Покупка продуктов", "Обед в кафе", "Продукты на неделю", "Такси до работы", "Крупная закупка"],
    }
    df = pd.DataFrame(data)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    return df


def test_basic_category_filtering(sample_transactions):
    """Тест базовой фильтрации по категории"""
    result = spending_by_category(transactions=sample_transactions, category="Супермаркеты", date="2021-05-01")

    # Проверки
    assert result["total_spending"] == 3000.0 + 2000.0
    assert len(result["transactions"]) == 2


def test_empty_result(sample_transactions):
    """Тест обработки отсутствия данных"""
    result = spending_by_category(
        transactions=sample_transactions, category="Несуществующая категория", date="2021-05-01"
    )

    assert result["total_spending"] == 0.0
    assert len(result["transactions"]) == 0


def test_invalid_date_format(sample_transactions):
    """Тест обработки неверного формата даты"""
    with pytest.raises(ValueError):
        spending_by_category(
            transactions=sample_transactions, category="Супермаркеты", date="2021/05/01"  # Неверный формат
        )
