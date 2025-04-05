import json
import logging
import os
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()


def greet() -> str:
    """Функция возвращает приветствие в зависимости от текущего времени суток"""
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        return "Доброе утро"
    elif 12 <= current_hour < 18:
        return "Добрый день"
    elif 18 <= current_hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_data_frame_from_excel_file(excel_file_path: str) -> dict:
    """Загружает данные из Excel файла и возвращает их в виде словаря."""
    try:
        # Загружаем Excel файл
        excel_data = pd.read_excel(excel_file_path, sheet_name=None)

        # Преобразуем в словарь, где ключи — имена листов, а значения — DataFrame
        return excel_data

    except Exception as e:
        print(f"Ошибка при загрузке файла: {e}")
        return {}


def get_cards(transactions: pd.DataFrame) -> list:
    """
    Анализирует список транзакций и возвращает информацию по каждой карте:
    - последние 4 цифры номера карты;
    - общая сумма расходов;
    - кешбэк (1 рубль на каждые 100 рублей).
    """
    card_data = {}

    for _, row in transactions.iterrows():
        # Пропускаем неуспешные транзакции и некорректные данные
        if row["Статус"] != "OK" or pd.isna(row["Номер карты"]):
            continue

        # Обработка номера карты
        card_number = str(row["Номер карты"]).strip().replace("*", "").replace(" ", "")
        if len(card_number) < 4:
            continue  # Пропускаем некорректные номера

        last_4_digits = card_number[-4:]

        # Обновляем данные карты
        if last_4_digits not in card_data:
            card_data[last_4_digits] = {"total_spent": 0.0, "cashback": 0}

        card_data[last_4_digits]["total_spent"] += row["Сумма операции"]
        card_data[last_4_digits]["cashback"] += row["Сумма операции"] // 100

    # Формируем результат
    result = [
        {"last_digits": last_4, "total_spent": round(card_info["total_spent"], 2), "cashback": card_info["cashback"]}
        for last_4, card_info in card_data.items()
    ]

    return result


def get_top_transaction(transactions: pd.DataFrame) -> list:
    """Функция Топ-5 транзакций по сумме платежа"""
    successful_transactions = transactions[transactions["Статус"] == "OK"]
    top_transactions = successful_transactions.sort_values(by="Сумма операции", ascending=False).head(5)

    top_transactions_list = [
        {
            "data": row["Дата операции"],
            "amount": row["Сумма операции"],
            "category": row["Категория"],
            "description": row["Описание"],
        }
        for _, row in top_transactions.iterrows()
    ]

    print(f"Топ транзакций: {top_transactions_list}")
    return top_transactions_list


def get_currency_rates(user_setting_path: str) -> list:
    """Функция получает стоимость для валют, указанных в файле настроек пользователя"""
    with open(user_setting_path, "r") as f:
        user_setting = json.load(f)

        # Берем только доллар и евро из JSON файла
        currencies = [currency for currency in user_setting.get("user_currencies", []) if currency in ["USD", "EUR"]]
        logging.info(f"Валюты для обработки: {currencies}")
        api_key = os.getenv("API_KEY")
        currency_rates = []

        for currency in currencies:
            url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{currency}"
            response = requests.get(url)
            data = response.json()

            # Логирование ответа
            logging.info(f"Ответ от API для {currency}: {data}")

            if "conversion_rates" in data:
                rate = round(data["conversion_rates"].get("RUB", 0.0), 2)
                currency_rates.append({"currency": currency, "rate": rate})

        return currency_rates


def get_stock_prices(user_settings_path: str) -> dict:
    """Получает цены акций через Marketstack API."""
    try:
        with open(user_settings_path, "r") as f:
            user_settings = json.load(f)
    except Exception as e:
        logging.error(f"Ошибка загрузки настроек: {e}")
        return {"stock_prices": []}

    stocks = user_settings.get("user_stocks", ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"])
    api_key = os.environ.get("API_STOCK")

    if not api_key:
        logging.error("Ключ API_STOCK не найден.")
        return {"stock_prices": []}

    stock_prices = []
    for stock in stocks:
        # Формируем URL для одной акции
        url = f"https://api.marketstack.com/v1/eod?access_key={api_key}&symbols={stock}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Проверяем структуру ответа
            if "data" not in data or not isinstance(data["data"], list):
                logging.warning(f"Некорректный ответ для {stock}: {data}")
                continue

            if len(data["data"]) == 0:
                logging.info(f"Нет данных для {stock}.")
                continue

            latest_data = data["data"][0]
            stock_prices.append(
                {
                    "stock": stock,
                    "price": latest_data.get("adj_close", latest_data.get("close")),
                    "date": latest_data.get("date"),
                }
            )

        except requests.exceptions.RequestException as e:
            logging.error(f"Ошибка запроса для {stock}: {str(e)}")

    return {"stock_prices": stock_prices}
