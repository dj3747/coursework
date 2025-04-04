import json
import logging
from datetime import datetime

import pandas as pd

from config import excel_file_path, user_settings_path
from src.utils import get_cards, get_currency_rates, get_stock_prices, get_top_transaction, greet

# Настроить логирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


def filter_transactions_by_date(transactions, start_date, end_date):
    """Фильтрация операций по диапазону дат"""
    return transactions[(transactions["date"] >= start_date) & (transactions["date"] <= end_date)]


def handle_request(date_time_str: str):
    """Обработка запроса веб-страницы"""
    try:
        date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
        logging.info("Начало выполнения программы с датой и временем: {date_time}")
    except ValueError as e:
        logging.error(f"Неправильный формат даты и времени: {e}")
        return

    logging.info("Начало выполнения программы")

    # Загрузить данные из Excel файла
    transactions_date_path = excel_file_path
    logging.info("Загрузка данных из файла: %s", transactions_date_path)
    transactions = pd.read_excel(transactions_date_path)

    # Преобразовать столбец с датами в формат datetime
    transactions["date"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    # Фильтровать операции по дате, устанавливая дату на первое число месяца и сбрасывая время на полночь
    start_date = date_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    filter_transactions = filter_transactions_by_date(transactions, start_date, date_time)

    # Загрузить данные из JSON файла
    logging.info("Загрузка данных из файла: %s", user_settings_path)

    # Собрать результаты
    result = {
        "greeting": greet(),  # Получить приветствие
        "cards": get_cards(filter_transactions),  # Получить карты
        "top_transactions": get_top_transaction(filter_transactions),  # Получить топ транзакций
        "currency_rates": get_currency_rates(user_settings_path),  # Получить валютные курсы
        "stock_prices": get_stock_prices(user_settings_path),  # Получить цены акций
    }

    logging.info("Результаты: %s", json.dumps(result, indent=4, ensure_ascii=False))

    result_json = json.dumps(result, indent=4, ensure_ascii=False)
    return result_json
