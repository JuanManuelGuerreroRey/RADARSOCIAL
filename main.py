import os
import logging
import random
import json
from telegram import Update, ChatMember
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler,
    filters, CallbackContext
)
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

# Claves directamente incluidas para asegurar funcionamiento
TOKEN = "8027791367:AAHOlycqUkBdVdM88dVBaIRr57piN3DRXR4"
GRUPO_ID = -1001169225264

# Diccionarios en memoria para simplificar la demo
interacciones = defaultdict(lambda: defaultdict(int))
nominaciones = defaultdict(list)
respuestas_auto = {
    "franco": "🇪🇸 ¡Arriba España!",
    "pro": "🤖 ¿Eres pro algo? ¡Yo soy pro-código!"
}

usuarios_cache = {}  # Para evitar recargar nombres siempre

# FUNCIONES

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🇪🇸 Bienvenido al Radar Social Bot.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Comandos disponibles:\n"
        "/pareja_dia\n/nominar @usuario\n/nominaciones\n/expulsar @usuario\n"
        "/compatibilidad @usuario\n/stats\n/help"
    )

async def pareja_dia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    members = [u for u in usuarios_cache.values()]
    if len(members) < 2:
        await update.message.reply_text("❗ No hay suficientes usuarios registrados.")
        return
    pareja = random.sample(members, 2)
    await update.message.reply_text(f"💘 Pareja del día: {pareja[0]} ❤️ {pareja[1]}")

async def enviar_pareja_automatica(context: CallbackContext):
    if len(usuarios_cache) >= 2:
        pareja = random.sample(list(usuarios_cache.values()), 2)
        msg = f"🎯 *Pareja del día automática*\n❤️ {pareja[0]} + {pareja[1]}"
        await context.bot.send_message(chat_id=GRUPO_ID, text=msg, parse_mode="Markdown")

async def nominar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Debes mencionar a alguien para nominar.")
        return
    nominado = context.args[0]
    user = update.effective_user.username or update.effective_user.first_name
    nominaciones[user].append(nominado)
    await update.message.reply_text(f"{nominado} ha sido nominado por {user} 🗳️")

async def ver_nominaciones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not nominaciones:
        await update.message.reply_text("Aún no hay nominaciones.")
        return
    texto = "📋 *Nominaciones:*\n"
    for nominador, lista in nominaciones.items():
        texto += f"👤 {nominador} nominó a: {', '.join(lista)}\n"
    await update.message.reply_text(texto, parse_mode="Markdown")

async def expulsar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Menciona a alguien para expulsar.")
        return
    expulsado = context.args[0]
    await update.message.reply_text(f"⛔ {expulsado} ha sido expulsado del Reality Show (ficticiamente).")

async def compatibilidad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Menciona a alguien para calcular compatibilidad.")
        return
    persona = context.args[0]
    porcentaje = random.randint(20, 100)
    await update.message.reply_text(f"💞 Tu compatibilidad con {persona} es del {porcentaje}%")

async def manejar_mensajes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower()
    for palabra, respuesta in respuestas_auto.items():
        if palabra in texto:
            await update.message.reply_text(respuesta)
            break
    user = update.effective_user
    usuarios_cache[user.id] = user.full_name

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conteo = defaultdict(int)
    for u in usuarios_cache.values():
        conteo[u] += 1
    ranking = sorted(conteo.items(), key=lambda x: x[1], reverse=True)
    texto = "📊 Usuarios activos:\n"
    for i, (usuario, total) in enumerate(ranking[:10], 1):
        texto += f"{i}. {usuario}\n"
    await update.message.reply_text(texto)

# MAIN

def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("pareja_dia", pareja_dia))
    app.add_handler(CommandHandler("nominar", nominar))
    app.add_handler(CommandHandler("nominaciones", ver_nominaciones))
    app.add_handler(CommandHandler("expulsar", expulsar))
    app.add_handler(CommandHandler("compatibilidad", compatibilidad))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensajes))

    # Enviar pareja del día automáticamente cada hora
    app.job_queue.run_repeating(enviar_pareja_automatica, interval=3600, first=10)

    app.run_polling()

if __name__ == "__main__":
    main()
