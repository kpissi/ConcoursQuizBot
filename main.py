import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

USERS = {}

QUESTIONS = {
    "SVT": [
        {
            "q": "Quel organe permet la respiration ?",
            "options": ["Cœur", "Poumon", "Foie", "Rein"],
            "answer": "Poumon",
            "explication": "Les poumons permettent la respiration."
        },
        {
            "q": "Le sang est principalement composé de ?",
            "options": ["Air", "Os", "Eau", "Graisse"],
            "answer": "Eau",
            "explication": "Le plasma sanguin est majoritairement composé d’eau."
        }
    ],
    "FRANÇAIS": [
        {
            "q": "Pluriel de cheval ?",
            "options": ["Chevals", "Chevaux", "Chevales", "Chevaus"],
            "answer": "Chevaux",
            "explication": "Cheval → Chevaux (irrégulier)."
        }
    ]
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bienvenue ! Quel est ton nom ?")
    context.user_data["step"] = "ASK_NAME"

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Démarrer\n"
        "/menu - Choisir une matière\n"
        "/score - Voir mon score"
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🧬 SVT", callback_data="SVT")],
        [InlineKeyboardButton("📘 FRANÇAIS", callback_data="FRANÇAIS")],
    ]
    await update.message.reply_text(
        "📚 Choisis une matière :",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("step") == "ASK_NAME":
        name = update.message.text
        USERS[update.effective_user.id] = {"name": name, "score": 0}
        context.user_data["step"] = None
        await update.message.reply_text(
            f"Bienvenue {name} ✅\nUtilise /menu pour commencer."
        )

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    subject = query.data

    question = random.choice(QUESTIONS[subject])
    context.user_data["answer"] = question["answer"]

    keyboard = [
        [InlineKeyboardButton(opt, callback_data=f"ANSWER|{opt}")]
        for opt in question["options"]
    ]

    await query.edit_message_text(
        f"📝 {subject}\n\n{question['q']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_answer = query.data.split("|")[1]
    correct = context.user_data["answer"]

    user = USERS.get(query.from_user.id)

    if user_answer == correct:
        user["score"] += 1
        await query.edit_message_text("✅ Bonne réponse !")
    else:
        await query.edit_message_text(f"❌ Mauvaise réponse.\nRéponse : {correct}")

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = USERS.get(update.effective_user.id)
    if not user:
        await update.message.reply_text("Utilise /start d’abord.")
        return
    await update.message.reply_text(
        f"📊 {user['name']} — Score : {user['score']}"
    )

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("score", score))
    app.add_handler(CallbackQueryHandler(handle_answer, pattern="^ANSWER"))
    app.add_handler(CallbackQueryHandler(handle_choice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
