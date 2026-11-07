import json
import os
import logging
from dotenv import load_dotenv

load_dotenv()
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)


TOKEN = os.getenv("BOT_TOKEN")

FILE_NAME = "user.json"

logging.basicConfig(
    level=logging.INFO
)


# ---------- Работа с JSON ----------

def load_users():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}


def save_users(users):
    with open(FILE_NAME, "w", encoding="utf-8") as file:
        json.dump(
            users,
            file,
            ensure_ascii=False,
            indent=4
        )


# ---------- /start ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = str(update.effective_user.id)

    users = load_users()

    if user_id in users:
        await update.message.reply_text(
            "Ты уже зарегистрирован ✅\n"
            "Используй /profile чтобы посмотреть данные."
        )
        return


    context.user_data["registration"] = True
    context.user_data["step"] = "name"


    await update.message.reply_text(
        "👋 Привет!\n"
        "Как тебя зовут?"
    )



# ---------- Получение имени и предмета ----------

async def get_info(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if "registration" not in context.user_data:
        return


    text = update.message.text


    if context.user_data["step"] == "name":

        context.user_data["name"] = text
        context.user_data["step"] = "subject"


        await update.message.reply_text(
            "Отлично! 📚\n"
            "Какой твой любимый предмет?"
        )


    elif context.user_data["step"] == "subject":

        name = context.user_data["name"]
        subject = text


        users = load_users()

        user_id = str(update.effective_user.id)


        users[user_id] = {
            "name": name,
            "subject": subject
        }


        save_users(users)


        context.user_data.clear()


        keyboard = [
            [
                InlineKeyboardButton(
                    "⏱ Помодоро",
                    callback_data="pomodoro"
                )
            ],
            [
                InlineKeyboardButton(
                    "💡 Совет дня",
                    callback_data="tip"
                )
            ],
            [
                InlineKeyboardButton(
                    "📚 Предметы",
                    callback_data="subjects"
                )
            ]
        ]


        await update.message.reply_text(
            "Готово! ✅\n"
            "Твои данные сохранены.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )



# ---------- /profile ----------

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):

    users = load_users()

    user_id = str(update.effective_user.id)


    if user_id in users:

        name = users[user_id]["name"]
        subject = users[user_id]["subject"]


        await update.message.reply_text(
            f"👤 Профиль\n\n"
            f"Имя: {name}\n"
            f"📚 Любимый предмет: {subject}"
        )


    else:

        await update.message.reply_text(
            "Профиль не найден ❌\n"
            "Напиши /start"
        )



# ---------- Кнопки ----------

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()


    if query.data == "pomodoro":

        await query.message.reply_text(
            "⏱ Помодоро:\n"
            "Учись 25 минут без отвлечений!"
        )


    elif query.data == "tip":

        await query.message.reply_text(
            "💡 Совет:\n"
            "Лучше заниматься каждый день понемногу."
        )


    elif query.data == "subjects":

        await query.message.reply_text(
            "📚 Предметы:\n"
            "Математика\n"
            "Химия\n"
            "Информатика\n"
            "Английский язык"
        )



# ---------- Запуск ----------

def main():

    app = ApplicationBuilder().token(TOKEN).build()


    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("profile", profile)
    )


    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            get_info
        )
    )


    app.add_handler(
        CallbackQueryHandler(buttons)
    )


    print("УчёбаБОТ запущен!")


    app.run_polling()



if __name__ == "__main__":
    main()