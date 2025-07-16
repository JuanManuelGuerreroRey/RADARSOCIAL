import json
import logging
import os
import random
from collections import defaultdict, Counter
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Configuración básica
TOKEN = "8027791367:AAHOlycqUkBdVdM88dVBaIRr57piN3DRXR4"
GROUP_ID = -1001169225264

# Interacciones por usuario
interacciones = defaultdict(lambda: defaultdict(int))
mensaje_count = 0
ultimo_mensaje_id = None
pareja_anterior = None

# Nominaciones y votos para modo Reality
nominaciones = defaultdict(set)
votaciones = Counter()

# Cargar interacciones anteriores
try:
    with open("interacciones.json", "r") as f:
        interacciones.update(json.load(f))
except FileNotFoundError:
    pass

# Guardar datos periódicamente
def guardar_datos():
    with open("interacciones.json", "w") as f:
        json.dump(interacciones, f)

# Registro de mensajes
async def registrar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global mensaje_count, ultimo_mensaje_id

    if update.message and update.message.from_user:
        usuario = update.message.from_user.first_name
        mensaje_count += 1

        if update.message.reply_to_message and update.message.reply_to_message.from_user:
            receptor = update.message.reply_to_message.from_user.first_name
            interacciones[usuario][receptor] += 1

        texto = update.message.text.lower()

        # Frases automáticas
        respuestas = {
            "franco": "Arriba España 🤚",
            "bro": ["Masivo bro", "Siempre ganando", "Hay niveles bro", "Fucking panzas"],
            "moros": "Moros no, España no es un zoo.",
            "negros": "No soy racista, soy ordenado. Dios creó el mundo con continentes por algo.",
            "charo": [
                "Sola y borracha quiero llegar a casa",
                "La culpa es del heteropatriarcado",
                "Pedro Sánchez es muy guapo"
            ]
        }

        for palabra, respuesta in respuestas.items():
            if palabra in texto:
                await update.message.reply_text(random.choice(respuesta) if isinstance(respuesta, list) else respuesta)
                break

        # Pareja del día automática
        if mensaje_count % 100 == 0:
            await pareja_del_dia(update, context)

        guardar_datos()

# Comandos básicos
async def top_interacciones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "🤝 Interacciones entre usuarios:\n"
    ranking = []
    for usuario, otros in interacciones.items():
        for receptor, cantidad in otros.items():
            ranking.append((cantidad, usuario, receptor))

    ranking.sort(reverse=True)
    for cantidad, usuario, receptor in ranking[:15]:
        msg += f"{usuario} → {receptor}: {cantidad}\n"
    await update.message.reply_text(msg)

async def pareja_del_dia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pareja_anterior
    top = []
    for usuario, otros in interacciones.items():
        for receptor, count in otros.items():
            top.append((count, usuario, receptor))
    top.sort(reverse=True)

    if top:
        count, u1, u2 = top[0]
        if pareja_anterior != (u1, u2):
            pareja_anterior = (u1, u2)
            msg = f"💘 Pareja del día: {u1} & {u2} ({count} interacciones)"
            await context.bot.send_message(chat_id=GROUP_ID, text=msg)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contador = defaultdict(int)
    for usuario, otros in interacciones.items():
        total = sum(otros.values())
        contador[usuario] += total

    top = sorted(contador.items(), key=lambda x: x[1], reverse=True)
    msg = "📊 Principales usuarios activos:\n"
    for user, count in top[:10]:
        msg += f"{user}: {count} mensajes\n"
    await update.message.reply_text(msg)

async def menciones_juan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contador = defaultdict(int)
    for usuario, otros in interacciones.items():
        contador[usuario] += otros.get("Juan", 0)

    top = sorted(contador.items(), key=lambda x: x[1], reverse=True)
    msg = "👤 Menciones a Juan:\n"
    for user, count in top:
        msg += f"{user}: {count} veces\n"
    await update.message.reply_text(msg)

# Reality Show: nominaciones
async def nominar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nominado = " ".join(context.args)
    if not nominado:
        await update.message.reply_text("❗ Debes escribir el nombre de a quién nominas.")
        return

    nominador = update.message.from_user.first_name
    if nominado == nominador:
        await update.message.reply_text("❌ No puedes nominarte a ti mismo.")
        return

    if nominado in nominaciones[nominador]:
        await update.message.reply_text("⚠️ Ya has nominado a esa persona.")
        return

    nominaciones[nominador].add(nominado)
    votaciones[nominado] += 1
    await update.message.reply_text(f"✅ {nominador} ha nominado a {nominado}.")

async def ranking_nominados(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📉 Ranking de nominaciones:\n"
    for user, count in votaciones.most_common():
        msg += f"{user}: {count} nominaciones\n"
    await update.message.reply_text(msg)

# Setup del bot
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, registrar_mensaje))
    app.add_handler(CommandHandler("interacciones", top_interacciones))
    app.add_handler(CommandHandler("pareja_dia", pareja_del_dia))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("menciones_juan", menciones_juan))
    app.add_handler(CommandHandler("nominar", nominar))
    app.add_handler(CommandHandler("nominaciones", ranking_nominados))

    print("Bot corriendo...")
    app.run_polling()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
