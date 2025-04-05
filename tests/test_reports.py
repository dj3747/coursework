import pytest
from unittest.mock import patch, mock_open, MagicMock
import pandas as pd
import json
from datetime import datetime
from src.reports import spending_by_category


# Тесты для spending_by_category
@pytest.fixture
def sample_transactions():
    data = {
        "Дата операции": ["2023-01-01 12:00:00", "2023-01-15 09:30:00", "2023-02-01 18:15:00"],
        "Категория": ["Супермаркеты", "Рестораны", "Супермаркеты"],
        "Сумма операции": [-1000.0, -2000.0, -1500.0],
        "Описание": ["Покупки", "Обед", "Продукты"]
    }
    df = pd.DataFrame(data)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%Y-%m-%d %H:%M:%S")
    return df



def test_spending_by_category_success(sample_transactions):
    with patch("pandas.read_excel", return_value=sample_transactions):
        result = spending_by_category(
            transactions=sample_transactions,
            category="Супермаркеты",
            start_date="2023-01-01",
            end_date="2023-01-31"
        )
        assert result["total_spending"] == -1000.0
        assert len(result["transactions"]) == 1


def test_spending_by_category_empty_result(sample_transactions):
    result = spending_by_category(
        transactions=sample_transactions,
        category="Транспорт",
        start_date="2023-01-01",
        end_date="2023-01-31"
    )

    assert result["total_spending"] == 0.0
    assert len(result["transactions"]) == 0


def test_spending_by_category_date_filtering(sample_transactions):
    result = spending_by_category(
        transactions=sample_transactions,
        category="Супермаркеты",
        start_date="2023-01-01",
        end_date="2023-02-28"
    )

    assert result["total_spending"] == -2500.0
    assert len(result["transactions"]) == 2


# Тест обработки ошибок формата даты
def test_spending_by_category_invalid_date():
    with pytest.raises(ValueError), \
            patch("logging.error") as mocked_logging:
        spending_by_category(
            transactions=pd.DataFrame(),
            category="Тест",
            start_date="invalid-date",
            end_date="2023-01-01"
        )

        mocked_logging.assert_called_with("Некорректный формат даты")


