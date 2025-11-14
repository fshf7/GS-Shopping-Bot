from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
)
from google_sheets import add_order_to_sheet
from telegram.helpers import escape_markdown
from config import ADMIN_ID

# Состояния диалога
NAME, CONTACT, DATA, QUANTITY, CONFIRM = range(5)


# --- 1. Начало диалога ---
async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите ваше имя:")
    return NAME


# --- 2. Имя → Контакт ---
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Отлично! Теперь введите ваш контакт (телефон или @username):")
    return CONTACT


# --- 3. Контакт → Данные о товаре ---
async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["contact"] = update.message.text
    await update.message.reply_text(
        "Теперь пришлите ссылку, название или фото товара:"
    )
    return DATA


# --- 4. Получаем описание товара (текст или фото) ---
async def get_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:  # пользователь отправил фото
        photo = update.message.photo[-1]  # берём фото в наилучшем качестве
        context.user_data["product_type"] = "photo"
        context.user_data["product_data"] = photo.file_id
    else:  # пользователь отправил текст (ссылку или описание)
        context.user_data["product_type"] = "text"
        context.user_data["product_data"] = update.message.text

    await update.message.reply_text("Введите количество:")
    return QUANTITY


# --- 5. Количество → Подтверждение ---
async def get_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["quantity"] = update.message.text

    # формируем сводку
    summary = (
        f"Проверьте данные:\n\n"
        f"Имя: {context.user_data['name']}\n"
        f"Контакт: {context.user_data['contact']}\n"
        f"Товар: {('Фото' if context.user_data['product_type'] == 'photo' else context.user_data['product_data'])}\n"
        f"Количество: {context.user_data['quantity']}\n\n"
        f"Все верно? (да/нет)"
    )
    await update.message.reply_text(summary)
    return CONFIRM


# --- 6. Подтверждение ---
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if text == "да":
        context.user_data["user_id"] = update.effective_user.id  # ✅ сохраняем ID клиента
        # Сохраняем заказ в Google Sheets
        add_order_to_sheet(context.user_data)
        # Сообщаем клиенту
        await update.message.reply_text(
            "✅ Ваш заказ принят! Менеджер скоро свяжется с вами. Спасибо! 💬"
        )
        # Формируем сообщение для владельца
        message = (
            f"📦 *Новый заказ!*\n\n"
            f"👤 Имя: {context.user_data['name']}\n"
            f"📞 Контакт: {context.user_data['contact']}\n"
            f"📦 Товар: {('Фото' if context.user_data['product_type'] == 'photo' else context.user_data['product_data'])}\n"
            f"🔢 Количество: {context.user_data['quantity']}\n"
            f"🆔 user_id: `{context.user_data['user_id']}`"
        )

        safe_message = escape_markdown(message, version=2)
        
        keyboard = [
            [InlineKeyboardButton("💬 Ответить клиенту", callback_data=f"reply_{context.user_data['user_id']}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if context.user_data["product_type"] == "photo":
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=context.user_data["product_data"],
                caption=safe_message,
                reply_markup=reply_markup,
                parse_mode="MarkdownV2"
            )
        else:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=safe_message,
                reply_markup=reply_markup,
                parse_mode="MarkdownV2"
            ) 
    else:
        await update.message.reply_text("Окей, заказ отменён.")

    return ConversationHandler.END


# --- 7. Отмена ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Заказ отменён.")
    return ConversationHandler.END


# --- 8. Регистрируем обработчик ---
def get_order_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("order", start_order)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact)],
            DATA: [
                MessageHandler(
                    (filters.TEXT | filters.PHOTO) & ~filters.COMMAND, get_data
                )
            ],
            QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_quantity)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
