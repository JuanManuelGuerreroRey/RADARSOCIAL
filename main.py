import json
import os
import random
from telegram import Update, ChatMember
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from datetime import datetime
import logging
from collections import defaultdict

# Variables ya integradas directamente
BOT_TOKEN = "8027791367:AAHOlycqUkBdVdM88dVBaIRr57piN3DRXR4"
GRUPO_ID = -1001169225264

# Inicializar registros de interacciones
INTERACCIONES_FILE = "interacciones.json"
if os.path.exists(INTERACCIONES_FILE):
    with open(INTERACCIONES_FILE, "r", encoding="utf-8") as f:
        interacciones = json.load(f)
else:
    interacciones = defaultdict(int)

logging.basicConfig(level=logging.INFO)

# Guardar interacciones
def guardar_interacciones():
    with open(INTERACCIONES_FILE, "w", encoding="utf-8") as f:
        json.dump(interacciones, f, indent=2, ensure_ascii=False)

# Pareja del día
usuarios_cache = []

async def pareja(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    members = await context.bot.get_chat_administrators(chat.id)
    all_members = [admin.user for admin in members if not admin.user.is_bot]
    if len(all_members) < 2:
        await update.message.reply_text("No hay suficientes usuarios.")
        return
    pareja = random.sample(all_members, 2)
    texto = f"❤️ Hoy la pareja del día es: {pareja[0].mention_html()} y {pareja[1].mention_html()} ❤️"
    await context.bot.send_message(chat.id, texto, parse_mode="HTML")

# Envío automático cada hora
async def enviar_pareja_automatica(context: ContextTypes.DEFAULT_TYPE):
    chat_id = GRUPO_ID
    try:
        members = await context.bot.get_chat_administrators(chat_id)
        all_members = [admin.user for admin in members if not admin.user.is_bot]
        if len(all_members) >= 2:
            pareja = random.sample(all_members, 2)
            texto = f"💘 Pareja automática: {pareja[0].mention_html()} + {pareja[1].mention_html()}"
            await context.bot.send_message(chat_id, texto, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Error al enviar pareja automática: {e}")

# Compatibilidad
async def compatibilidad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("Usa: /compatibilidad @usuario1 @usuario2")
        return
    u1, u2 = context.args
    nivel = random.randint(0, 100)
    texto = f"💞 Compatibilidad entre {u1} y {u2}: {nivel}%"
    await update.message.reply_text(texto)

# Nominados
nominados = set()

async def nominar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usa: /nominar @usuario")
        return
    usuario = context.args[0]
    nominados.add(usuario)
    await update.message.reply_text(f"{usuario} ha sido nominado 📛")

async def ver_nominados(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not nominados:
        await update.message.reply_text("No hay nominados.")
    else:
        await update.message.reply_text("📢 Nominados:\n" + "\n".join(nominados))

async def expulsar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usa: /expulsar @usuario")
        return
    usuario = context.args[0]
    if usuario in nominados:
        nominados.remove(usuario)
        await update.message.reply_text(f"{usuario} ha sido expulsado 🧹")
    else:
        await update.message.reply_text("Ese usuario no está nominado.")

# Interacción automática por palabras clave
PALABRAS_CLAVE = {
    "franco": "¡Arriba España 🇪🇸!",
    "pro": "¡Tú sí que sabes!",
    "viva": "¡Viva España!"
}

async def detectar_mensajes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower()
    for palabra, respuesta in PALABRAS_CLAVE.items():
        if palabra in texto:
            await update.message.reply_text(respuesta)
            break
    # Registrar interacción
    usuario = update.effective_user.username or update.effective_user.first_name
    interacciones[usuario] = interacciones.get(usuario, 0) + 1
    guardar_interacciones()

# Ranking
async def ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not interacciones:
        await update.message.reply_text("Aún no hay interacciones registradas.")
        return
    ordenado = sorted(interacciones.items(), key=lambda x: x[1], reverse=True)
    texto = "📊 Ranking de actividad:\n"
    for i, (usuario, puntos) in enumerate(ordenado[:10], 1):
        texto += f"{i}. {usuario}: {puntos} pts\n"
    await update.message.reply_text(texto)

# Start y help
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Bienvenido al Radar Social Bot!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
Comandos disponibles:
/start - Iniciar bot
/help - Ayuda
/ranking - Ver ranking de actividad
/pareja - Mostrar pareja del día
/compatibilidad @u1 @u2 - Ver compatibilidad
/nominar @usuario - Nominar a alguien
/nominados - Ver nominados
/expulsar @usuario - Expulsar nominado
""")

# Main
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ranking", ranking))
    app.add_handler(CommandHandler("pareja", pareja))
    app.add_handler(CommandHandler("compatibilidad", compatibilidad))
    app.add_handler(CommandHandler("nominar", nominar))
    app.add_handler(CommandHandler("nominados", ver_nominados))
    app.add_handler(CommandHandler("expulsar", expulsar))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), detectar_mensajes))

    # Pareja automática cada 1 hora
    app.job_queue.run_repeating(enviar_pareja_automatica, interval=3600, first=10)

    print("Bot corriendo...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
