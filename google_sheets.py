import os
import json

# === Создание credentials.json из переменной окружения ===
creds_env = os.getenv("GOOGLE_CREDENTIALS_JSON")

if creds_env:
    try:
        creds_path = "credentials.json"

        try:
            # Попытка распарсить как JSON
            parsed = json.loads(creds_env)
            with open(creds_path, "w", encoding="utf-8") as f:
                json.dump(parsed, f)
        except Exception:
            # Если JSON не парсится — просто записываем строку (на случай base64)
            with open(creds_path, "w", encoding="utf-8") as f:
                f.write(creds_env)

        print("Google credentials file created from env variable.")
    except Exception as e:
        print("Failed to create credentials.json from env:", e)


import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Настройки Google API
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_FILE = "credentials.json"

SPREADSHEET_ID = "1s5EkZy8G0prIxoiKJbVUq2zfhXyygnr5_mIBcPOg0XA"


# === Подключение к Google Sheet ===
def connect_to_sheet():
    creds = Credentials.from_service_account_file(SERVICE_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    return sheet


# === Добавление строки ===
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
