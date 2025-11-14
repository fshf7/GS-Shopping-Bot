# handlers/admin.py
from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler, CallbackQueryHandler, CommandHandler, MessageHandler, filters
)
import os
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# состояния
WAITING_REPLY = range(1)

# --- Обработка нажатия на кнопку "Ответить клиенту" ---
async def handle_reply_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != ADMIN_ID:
        await query.edit_message_text("❌ У вас нет доступа к этой функции.")
        return ConversationHandler.END

    # достаём user_id из callback_data
    user_id = int(query.data.split("_")[1])
    context.user_data["reply_to"] = user_id

    await query.message.reply_text("✉️ Напиши сообщение, которое нужно отправить клиенту:")
    return WAITING_REPLY


# --- Ожидание текста от владельца ---
async def send_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    user_id = context.user_data.get("reply_to")

    if not user_id:
        await update.message.reply_text("⚠️ Ошибка: не найден получатель.")
        return ConversationHandler.END

    # Отправляем клиенту
    await context.bot.send_message(
        chat_id=user_id,
        text=f"💬 Сообщение от менеджера:\n\n{message}"
    )

    await update.message.reply_text("✅ Сообщение отправлено клиенту.")
    context.user_data.pop("reply_to", None)
    return ConversationHandler.END


# --- Если отменил ---
async def cancel_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Ответ отменён.")
    return ConversationHandler.END


# --- Создаём ConversationHandler ---
def get_admin_reply_handler():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_reply_button, pattern=r"^reply_\d+$")],
        states={
            WAITING_REPLY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, send_reply)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_reply)],
        name="admin_reply_conversation",
    )
