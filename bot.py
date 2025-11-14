from telegram.ext import Application, CommandHandler
from handlers.order import get_order_handler
from config import TOKEN

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='telegram')

async def start(update, context):
    await update.message.reply_text(
        "Привет! 👋\n"
        "Я бот для оформления заказов 🚚\n\n"
        "Чтобы оформить заказ — напиши /order.\n"
        "Для отмены — /cancel."
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(get_order_handler())

    print("✅ Бот запущен... (нажми Ctrl+C для остановки)")
    app.run_polling()

if __name__ == "__main__":
    main()
