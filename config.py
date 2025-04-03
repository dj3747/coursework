import os

# Определение корневой директории проекта
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Путь к файлу Excel
excel_file_path = os.path.join(ROOT_DIR, 'data', 'operations.xlsx')
user_settings = os.path.join(ROOT_DIR, 'data', 'user_settings.json')
