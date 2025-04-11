import json
import logging
from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import requests

from src.utils import (get_cards,
                       get_currency_rates,
                       get_data_frame_from_excel_file,
                       get_stock_prices,
                       get_top_transaction,
                       greet)

logging.basicConfig(level=logging.INFO)


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


@pytest.fixture
def mock_settings_file(tmp_path):
    """Создает временный файл с настройками."""
    settings_path = tmp_path / "settings.json"
    settings_data = {"user_stocks": ["AAPL"]}
    settings_path.write_text(json.dumps(settings_data))
    return str(settings_path)


@patch("src.utils.requests.get")
def test_get_stock_prices_invalid_json(mock_get, mock_settings_file, mock_api_key):
    """Тест обработки некорректного JSON от API."""

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"invalid_data": "something"}
    mock_get.return_value = mock_response

    result = get_stock_prices(mock_settings_file)

    assert result == {"stock_prices": []}
    mock_get.assert_called_once()


@pytest.fixture(scope="function")
def mock_api_key(monkeypatch):
    """Устанавливает mock API key."""
    monkeypatch.setenv("API_KEY", "test_api_key")


@pytest.fixture(scope="function")
def mock_currency_settings_file(tmp_path):
    """Создает временный файл с настройками для валют."""
    settings_path = tmp_path / "currency_settings.json"
    settings_data = {"user_currencies": ["USD", "EUR"]}
    settings_path.write_text(json.dumps(settings_data))
    return str(settings_path)


@pytest.mark.usefixtures("mock_api_key")
@patch("src.utils.requests.get")
def test_get_currency_rates_api_error(mock_get, mock_currency_settings_file):
    """Тест обработки ошибки API."""

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
    mock_get.return_value = mock_response

    result = get_currency_rates(mock_currency_settings_file)
    assert result == []
    mock_get.assert_called()
