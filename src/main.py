import logging
from idlelib.iomenu import errors

import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import excel_file_path
from src.reports import spending_by_category
from src.services import analyze_cashback_categories, load_data_from_excel, save_result_to_file
from views import handle_request

# Настроить логирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


def main():
    """Вызов основной функции"""

    date_time_str = "2021-12-26 22:09:56"
    result_json = handle_request(date_time_str)
    print("Результаты веб-запроса:", result_json)

    # Вызов функции spending_by_category
    logging.info("Начало выполнения скрипта для анализа трат")
    data_path = excel_file_path
    logging.info(f"Загрузка данных из файла: {data_path}")

    # Загрузить данные и преобразовать в DataFrame
    transactions = pd.read_excel(data_path)

    transactions["Дата операции"] = pd.to_datetime(
        transactions["Дата операции"],
        format="%d.%m.%Y %H:%M:%S",
        errors="coerce"
    )

    report = spending_by_category(
        transactions, category="Супермаркеты", start_date="2021-01-01", end_date="2021-12-31"
    )
    logging.info("Генерация отчета завершена")
    print(report)

    # Вызов функций из модуля service
    logging.info("Начало выполнения скрипта для анализа кэшбэка")
    transactions = load_data_from_excel(data_path)
    year_input = 2021
    month_input = 3
    cashback_results = analyze_cashback_categories(transactions, year_input, month_input)

    json_output_path = "../data/cashback_results.json"
    save_result_to_file(cashback_results, json_output_path)

    logging.info("Генерация отчета завершена")
    print(cashback_results)

    logging.info("Конец выполнения скрипта")


if __name__ == "__main__":
    main()
