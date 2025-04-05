from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd

from src.utils import get_cards, get_data_frame_from_excel_file, get_top_transaction, greet


# Тесты для greet()
def test_greet():
    # Тестирование утреннего приветствия
    with patch("src.utils.datetime") as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 1, 1, 8, 0, 0)
        assert greet() == "Доброе утро"

    with patch("src.utils.datetime") as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 1, 1, 19, 0, 0)
        assert greet() == "Добрый вечер"


# Тесты для get_data_frame_from_excel_file()
@patch("pandas.read_excel")
def test_get_data_frame_from_excel(mock_read):
    mock_read.return_value = pd.DataFrame({"test": [1, 2, 3]})
    result = get_data_frame_from_excel_file("dummy.xlsx")
    assert "test" in result


# Тесты для get_cards()
def test_get_cards():
    mock_data = pd.DataFrame(
        {
            "Статус": ["OK", "FAILED", "OK"],
            "Номер карты": ["1234 5678 9012 3456", None, "**** 9999"],
            "Сумма операции": [-1000, 500, -250],
        }
    )

    result = get_cards(mock_data)
    assert len(result) == 2
    assert result[0]["cashback"] == 10


# Тесты для get_top_transaction()
def test_get_top_transaction():
    mock_data = pd.DataFrame(
        {
            "Статус": ["OK"] * 10,
            "Сумма операции": range(100, 1100, 100),
            "Категория": ["test"] * 10,
            "Описание": ["test"] * 10,
            "Дата операции": ["2023-01-01"] * 10,
        }
    )

    result = get_top_transaction(mock_data)
    assert len(result) == 5
    assert result[0]["amount"] == 1000


def test_get_stock_prices_success():
    """Тест успешного получения цен акций"""
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": [{"adj_close": 150.0, "close": 149.0, "date": "2023-10-01"}]}
