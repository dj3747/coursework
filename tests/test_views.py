from datetime import datetime
from unittest.mock import MagicMock, call, patch

import pandas as pd

import src.views
from src.views import filter_transactions_by_date, get_cards, get_stock_prices, handle_request


def test_filter_transactions_by_date():
    data = {"date": pd.date_range(start="2023-01-01", end="2023-01-10", freq="D"), "amount": range(10)}
    df = pd.DataFrame(data)
    filtered = filter_transactions_by_date(df, datetime(2023, 1, 3), datetime(2023, 1, 7))
    assert len(filtered) == 5


def test_handle_request_invalid_date():
    result = handle_request("invalid_date")
    assert result is None


def test_get_cards_empty_data():
    assert get_cards(pd.DataFrame()) == []


def test_get_stock_prices_file_not_found():
    prices = get_stock_prices("non_existent.json")
    assert "stock_prices" in prices


def test_handle_request_empty_datetime_string():
    """Тест с пустой строкой даты и времени."""
    with patch("src.views.logging.error") as mock_logging_error:
        date_time_str = ""  # Пустая строка
        handle_request(date_time_str)

        mock_logging_error.assert_called_once()
        call_args = mock_logging_error.call_args[0]
        assert "Неправильный формат даты и времени" in call_args[0]
        assert date_time_str in call_args[0]


def test_handle_request_none_datetime_string_returns_none():
    """Тест с None датой, проверяем, что возвращает None."""
    date_time_str = None
    result = handle_request(date_time_str)
    assert result is None  # Функция должна возвращать None в случае ошибки


def test_handle_request_invalid_datetime_format_logs_error():
    """Тест с некорректным форматом даты и времени, проверяем, что логируется ERROR."""
    with patch("src.views.logging.error") as mock_logging_error:
        date_time_str = "2024-01-01"  # Некорректный формат
        handle_request(date_time_str)

        mock_logging_error.assert_called_once()
        call_args = mock_logging_error.call_args[0]
        assert "Неправильный формат даты и времени" in call_args[0]
        assert date_time_str in call_args[0]


def test_handle_request_valid_datetime_logs_info():
    """Тест с корректной датой и временем, проверяем, что логируется INFO."""
    with patch.object(src.views, "logging", new_callable=MagicMock) as mock_logging:
        mock_logging.info.return_value = None  # Чтобы не сломать остальной код
        date_time_str = "2024-01-01 12:00:00"
        handle_request(date_time_str)

        expected_log_message = (
            f"Начало выполнения программы с датой и временем: {datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')}"
        )

        # Проверяем, что logging.info был вызван ХОТЯ БЫ ОДИН раз с ожидаемым сообщением
        calls = [call(expected_log_message)]
        mock_logging.info.assert_has_calls(calls, any_order=True)
