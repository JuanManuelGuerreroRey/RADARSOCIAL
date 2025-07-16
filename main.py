import os
import logging
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import random
import asyncio

# Configurar logging
logging.basicConfig(level=logging.INFO)

# TOKEN y GROUP_ID directamente en el código
TOKEN = "8027791367:AAHOlycqUkBdVdM88dVBaIRr57piN3DRXR4"
GROUP_ID = -1001169225264

# Variables globales para contar mensajes e interacciones
user_messages = Counter()
mentions_to_juan = Counter()
interactions = defaultdict(lambda: defaultdict(int))
last_sent_pareja = datetime.utcnow() - timedelta(hours=1)

# Frases automáticas
auto_replies = {
    "franco": "Arriba España 🤚",
    "bro": ["Masivo bro", "Siempre ganando", "Hay niveles bro", "Fucking panzas"],
    "moros": "Moros no, España no es un zoo.",
    "negros": "No soy racista, soy ordenado. Dios creó el mundo en diversos continentes, por algo será.",
    "charo": ["Sola y borracha quiero llegar a casa", "La culpa es del Hetero-patriarcado", "Pedro Sánchez es muy guapo"]
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot operativo.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top_users = user_messages.most_common(10)
    msg = "📊 Top usuarios activos:
" + "
".join([f"{user}: {count} mensajes" for user, count in top_users])
    await update.message.reply_text(msg)

async def menciones_juan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not mentions_to_juan:
        await update.message.reply_text("Nadie ha mencionado a Juan todavía.")
        return
    ranking = sorted(mentions_to_juan.items(), key=lambda x: x[1], reverse=True)
    msg = "📣 Menciones a Juan:
" + "
".join([f"{user}: {count} menciones" for user, count in ranking])
    await update.message.reply_text(msg)

async def pareja_dia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await enviar_pareja(context.bot)

async def reality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pairs = []
    for user1 in interactions:
        for user2 in interactions[user1]:
            score = interactions[user1][user2] + interactions[user2].get(user1, 0)
            if score > 0:
                pairs.append(((user1, user2), score))
    pairs.sort(key=lambda x: x[1], reverse=True)
    msg = "🎭 Compatibilidad social - Reality Show:
"
    for (user1, user2), score in pairs[:5]:
        msg += f"{user1} ❤️ {user2}: {score} interacciones
"
    await update.message.reply_text(msg)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user:
        return

    user = update.message.from_user.first_name
    text = update.message.text.lower()
    user_messages[user] += 1

    if "juan" in text:
        mentions_to_juan[user] += 1

    # Interacciones: si responde a otro mensaje
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        replied_user = update.message.reply_to_message.from_user.first_name
        interactions[user][replied_user] += 1

    # Respuestas automáticas
    for word, reply in auto_replies.items():
        if word in text:
            if isinstance(reply, list):
                await update.message.reply_text(random.choice(reply))
            else:
                await update.message.reply_text(reply)
            break

async def enviar_pareja(bot: Bot):
    global last_sent_pareja
    now = datetime.utcnow()
    if (now - last_sent_pareja).seconds < 3600:
        return
    last_sent_pareja = now
    max_pair = None
    max_score = 0
    for user1 in interactions:
        for user2, count in interactions[user1].items():
            total = count + interactions[user2].get(user1, 0)
            if total > max_score:
                max_score = total
                max_pair = (user1, user2)
    if max_pair:
        await bot.send_message(chat_id=GROUP_ID, text=f"💘 Pareja del día: {max_pair[0]} & {max_pair[1]}")

async def schedule_daily(bot: Bot):
    while True:
        await enviar_pareja(bot)
        await asyncio.sleep(3600)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("menciones_juan", menciones_juan))
    app.add_handler(CommandHandler("pareja_dia", pareja_dia))
    app.add_handler(CommandHandler("reality", reality))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))
    app.job_queue.run_repeating(lambda ctx: enviar_pareja(ctx.bot), interval=3600, first=10)
    app.run_polling()

if __name__ == "__main__":
    main()