from datetime import datetime

import pandas as pd

from src.views import filter_transactions_by_date, get_cards, get_stock_prices, greet, handle_request


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
