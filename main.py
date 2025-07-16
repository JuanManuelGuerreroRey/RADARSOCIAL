import logging
import json
import random
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, filters
)

# Variables ya definidas
TOKEN = "8027791367:AAHOlycqUkBdVdM88dVBaIRr57piN3DRXR4"
GROUP_ID = -1001169225264

# Archivos de datos
interacciones_file = "interacciones.json"
menciones_file = "menciones.json"

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Funciones auxiliares
def cargar_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def guardar_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def registrar_usuario(user_id, username):
    data = cargar_json(interacciones_file)
    data[str(user_id)] = username
    guardar_json(interacciones_file, data)

def registrar_mencion(user_id, username):
    data = cargar_json(menciones_file)
    if str(user_id) in data:
        data[str(user_id)]["conteo"] += 1
    else:
        data[str(user_id)] = {"username": username, "conteo": 1}
    guardar_json(menciones_file, data)

def obtener_pareja():
    usuarios = list(cargar_json(interacciones_file).items())
    if len(usuarios) < 2:
        return None
    return random.sample(usuarios, 2)

# Comandos
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    registrar_usuario(user.id, user.username or user.first_name)
    await update.message.reply_text("Bienvenido al Radar Social 👋")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Iniciar bot\n"
        "/pareja - Mostrar pareja del día\n"
        "/nominacion - Nominar a alguien\n"
        "/expulsion - Expulsar a alguien\n"
        "/compatibilidad - Compatibilidad entre usuarios\n"
        "/top - Ranking de menciones\n"
        "/help - Mostrar comandos"
    )

# Pareja del día
pareja_diaria = None

async def pareja(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pareja_diaria
    if not pareja_diaria:
        pareja_diaria = obtener_pareja()
    if pareja_diaria:
        u1, u2 = pareja_diaria
        await context.bot.send_message(chat_id=update.effective_chat.id,
            text=f"Pareja del día: @{u1[1]} ❤️ @{u2[1]}")
    else:
        await update.message.reply_text("No hay suficientes usuarios registrados.")

# Reality Show
nominados = []

async def nominacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usa /nominacion @usuario")
        return
    nominado = context.args[0]
    nominados.append(nominado)
    await update.message.reply_text(f"{nominado} ha sido nominado.")

async def expulsion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usa /expulsion @usuario")
        return
    expulsado = context.args[0]
    if expulsado in nominados:
        nominados.remove(expulsado)
        await update.message.reply_text(f"{expulsado} ha sido expulsado.")
    else:
        await update.message.reply_text(f"{expulsado} no está nominado.")

async def compatibilidad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Uso: /compatibilidad @user1 @user2")
        return
    p = random.randint(30, 100)
    await update.message.reply_text(f"Compatibilidad entre {context.args[0]} y {context.args[1]}: {p}%")

# Ranking de menciones
async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    datos = cargar_json(menciones_file)
    if not datos:
        await update.message.reply_text("No hay menciones registradas aún.")
        return
    ranking = sorted(datos.items(), key=lambda x: x[1]["conteo"], reverse=True)
    mensaje = "Ranking de menciones:\n"
    for i, (user_id, info) in enumerate(ranking[:10], 1):
        mensaje += f"{i}. @{info['username']} - {info['conteo']} menciones\n"
    await update.message.reply_text(mensaje)

# Pareja automática cada hora
async def enviar_pareja_automatica(context: ContextTypes.DEFAULT_TYPE):
    global pareja_diaria
    pareja_diaria = obtener_pareja()
    if pareja_diaria:
        u1, u2 = pareja_diaria
        await context.bot.send_message(chat_id=GROUP_ID,
            text=f"Pareja del día (automática): @{u1[1]} ❤️ @{u2[1]}")

# Mensajes y menciones
async def registrar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.entities:
        for ent in update.message.entities:
            if ent.type == "mention":
                username = update.message.text[ent.offset+1:ent.offset+ent.length]
                registrar_mencion(username, username)

# Main
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("pareja", pareja))
    app.add_handler(CommandHandler("nominacion", nominacion))
    app.add_handler(CommandHandler("expulsion", expulsion))
    app.add_handler(CommandHandler("compatibilidad", compatibilidad))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), registrar_mensaje))

    # Tarea repetida
    app.job_queue.run_repeating(enviar_pareja_automatica, interval=3600, first=10)

    print("Bot corriendo...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
