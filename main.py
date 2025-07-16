import logging import json import random import re from telegram import Update from telegram.ext import ( ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters )

Token y grupo directamente incluidos

TOKEN = "8027791367:AAHOlycqUkBdVdM88dVBaIRr57piN3DRXR4" GROUP_ID = -1001169225264

interactions_file = "interacciones.json"

Configurar logging

logging.basicConfig( format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO )

====================================

Funciones auxiliares

====================================

def cargar_interacciones(): try: with open(interactions_file, "r", encoding="utf-8") as f: return json.load(f) except: return {}

def guardar_interacciones(data): with open(interactions_file, "w", encoding="utf-8") as f: json.dump(data, f, indent=2, ensure_ascii=False)

def registrar_interaccion(user_id, username): data = cargar_interacciones() data[str(user_id)] = username guardar_interacciones(data)

def obtener_pareja(): usuarios = list(cargar_interacciones().items()) if len(usuarios) < 2: return None return random.sample(usuarios, 2)

====================================

Comandos

====================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): user = update.effective_user registrar_interaccion(user.id, user.username or user.first_name) await update.message.reply_text("👋 ¡Bienvenido al Radar Social!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text( "/start - Iniciar bot\n" "/pareja - Mostrar pareja del día\n" "/nominacion - Nominar a alguien (modo reality)\n" "/expulsion - Expulsar a alguien (modo reality)\n" "/compatibilidad - Ver compatibilidad\n" "/menciones_juan - Cuántas veces se menciona 'Juan'\n" "/ranking_menciones - Ranking de menciones\n" "/stats - Top usuarios activos\n" "/help - Ver comandos" )

💘 Pareja del día

pareja_diaria = None

async def pareja(update: Update, context: ContextTypes.DEFAULT_TYPE): global pareja_diaria if not pareja_diaria: pareja_diaria = obtener_pareja() if pareja_diaria: u1, u2 = pareja_diaria await context.bot.send_message(chat_id=update.effective_chat.id, text=f"💘 Pareja del día: @{u1[1]} ❤️ @{u2[1]}") else: await update.message.reply_text("❗ No hay suficientes usuarios para emparejar.")

👥 Modo Reality Show

nominados = []

async def nominacion(update: Update, context: ContextTypes.DEFAULT_TYPE): if not context.args: await update.message.reply_text("🔁 Especifica a quién nominas. Ej: /nominacion @usuario") return nominado = context.args[0] nominados.append(nominado) await update.message.reply_text(f"📣 Has nominado a {nominado}.")

async def expulsion(update: Update, context: ContextTypes.DEFAULT_TYPE): if not context.args: await update.message.reply_text("🔁 Especifica a quién expulsas. Ej: /expulsion @usuario") return expulsado = context.args[0] if expulsado in nominados: nominados.remove(expulsado) await update.message.reply_text(f"🛑 {expulsado} ha sido expulsado.") else: await update.message.reply_text(f"❌ {expulsado} no estaba nominado.")

💞 Compatibilidad

async def compatibilidad(update: Update, context: ContextTypes.DEFAULT_TYPE): if len(context.args) < 2: await update.message.reply_text("💡 Uso: /compatibilidad @user1 @user2") return compat = random.randint(30, 100) await update.message.reply_text(f"🔗 Compatibilidad entre {context.args[0]} y {context.args[1]}: {compat}%")

🧠 Stats y menciones

stats = {} menciones = {}

async def contar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE): user = update.effective_user username = user.username or user.first_name stats[username] = stats.get(username, 0) + 1 text = update.message.text.lower() if "juan" in text: menciones[username] = menciones.get(username, 0) + text.count("juan")

# Respuestas automáticas
if "franco" in text:
    await update.message.reply_text("Arriba España 🤚")
if "bro" in text:
    frases_bro = ["Masivo bro", "Siempre ganando", "Hay niveles bro", "Fucking panzas"]
    await update.message.reply_text(random.choice(frases_bro))
if "moros" in text:
    await update.message.reply_text("Moros no, España no es un zoo.")
if "negros" in text:
    await update.message.reply_text("No soy racista, soy ordenado. Dios creó continentes por algo.")
if "charo" in text:
    frases_charo = ["Sola y borracha quiero llegar a casa", "La culpa es del heteropatriarcado", "Pedro Sánchez es muy guapo"]
    await update.message.reply_text(random.choice(frases_charo))

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE): ranking = sorted(stats.items(), key=lambda x: x[1], reverse=True) msg = "📊 Principales usuarios activos:\n" for user, count in ranking[:10]: msg += f"{user}: {count} mensajes\n" await update.message.reply_text(msg)

async def menciones_juan(update: Update, context: ContextTypes.DEFAULT_TYPE): ranking = sorted(menciones.items(), key=lambda x: x[1], reverse=True) msg = "📈 Menciones a Juan por usuario:\n" for user, count in ranking: msg += f"{user}: {count}\n" await update.message.reply_text(msg)

🔁 Pareja automática cada hora

async def enviar_pareja_automatica(context: ContextTypes.DEFAULT_TYPE): global pareja_diaria pareja_diaria = obtener_pareja() if pareja_diaria: u1, u2 = pareja_diaria await context.bot.send_message(chat_id=GROUP_ID, text=f"💘 Pareja del día (automática): @{u1[1]} ❤️ @{u2[1]}")

====================================

Main

====================================

async def main(): app = ApplicationBuilder().token(TOKEN).build()

# Comandos
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("pareja", pareja))
app.add_handler(CommandHandler("nominacion", nominacion))
app.add_handler(CommandHandler("expulsion", expulsion))
app.add_handler(CommandHandler("compatibilidad", compatibilidad))
app.add_handler(CommandHandler("stats", stats_command))
app.add_handler(CommandHandler("menciones_juan", menciones_juan))

# Mensajes
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, contar_mensaje))

# JobQueue para pareja automática
app.job_queue.run_repeating(enviar_pareja_automatica, interval=3600, first=10)

print("Bot corriendo...")
await app.run_polling()

if name == "main": import asyncio asyncio.run(main())

