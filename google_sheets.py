import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Настройка доступа
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_FILE = "credentials.json"  # твой файл от Google
SPREADSHEET_ID = "1s5EkZy8G0prIxoiKJbVUq2zfhXyygnr5_mIBcPOg0XA"  # вставь ID таблицы из URL

# Авторизация
def connect_to_sheet():
    creds = Credentials.from_service_account_file(SERVICE_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1  # первая страница
    return sheet

# Добавление новой строки
def add_order_to_sheet(order_data):
    sheet = connect_to_sheet()
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([
        date,
        order_data.get("name"),
        order_data.get("contact"),
        order_data.get("product_data"),
        order_data.get("quantity"),
        order_data.get("product_type"),
        order_data.get("photo_id", "")
    ])
