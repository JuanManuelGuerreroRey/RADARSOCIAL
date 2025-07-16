import logging import os import json import random from collections import defaultdict, Counter from telegram import Update from telegram.ext import ( ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters )

TOKEN = "8027791367:AAHOlycqUkBdVdM88dVBaIRr57piN3DRXR4" GROUP_ID = -1001169225264

interactions_file = "interacciones.json" menciones_file = "menciones.json"

Configurar logging

logging.basicConfig( format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO )

====================================

Funciones auxiliares

====================================

def cargar_json(filename): try: with open(filename, "r", encoding="utf-8") as f: return json.load(f) except: return {}

def guardar_json(filename, data): with open(filename, "w", encoding="utf-8") as f: json.dump(data, f, indent=2, ensure_ascii=False)

def registrar_interaccion(user_id, username): data = cargar_json(interactions_file) data[str(user_id)] = username guardar_json(interactions_file, data)

def obtener_pareja(): usuarios = list(cargar_json(interactions_file).items()) if len(usuarios) < 2: return None return random.sample(usuarios, 2)

def registrar_mencion(username): data = cargar_json(menciones_file) data[username] = data.get(username, 0) + 1 guardar_json(menciones_file, data)

def obtener_top_menciones(): data = cargar_json(menciones_file) return sorted(data.items(), key=lambda x: x[1], reverse=True)

====================================

Comandos

====================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): user = update.effective_user registrar_interaccion(user.id, user.username or user.first_name) await update.message.reply_text("👋 ¡Bienvenido al Radar Social!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text( "/start - Iniciar bot\n" "/pareja - Mostrar pareja del día\n" "/nominacion @usuario - Nominar a alguien\n" "/expulsion @usuario - Expulsar nominado\n" "/compatibilidad @u1 @u2 - Ver compatibilidad\n" "/top - Ver ranking de menciones\n" "/help - Ver comandos" )

💘 Pareja del día

pareja_diaria = None

async def pareja(update: Update, context: ContextTypes.DEFAULT_TYPE): global pareja_diaria if not pareja_diaria: pareja_diaria = obtener_pareja() if pareja_diaria: u1, u2 = pareja_diaria await context.bot.send_message(chat_id=update.effective_chat.id, text=f"💘 Pareja del día: @{u1[1]} ❤️ @{u2[1]}") else: await update.message.reply_text("❗ No hay suficientes usuarios para emparejar.")

👥 Modo Reality Show

nominados = []

async def nominacion(update: Update, context: ContextTypes.DEFAULT_TYPE): if not context.args: await update.message.reply_text("🔁 Especifica a quién nominas. Ej: /nominacion @usuario") return nominado = context.args[0] nominados.append(nominado) await update.message.reply_text(f"📣 Has nominado a {nominado}.")

async def expulsion(update: Update, context: ContextTypes.DEFAULT_TYPE): if not context.args: await update.message.reply_text("🔁 Especifica a quién expulsas. Ej: /expulsion @usuario") return expulsado = context.args[0] if expulsado in nominados: nominados.remove(expulsado) await update.message.reply_text(f"🛑 {expulsado} ha sido expulsado.") else: await update.message.reply_text(f"❌ {expulsado} no estaba nominado.")

💞 Compatibilidad

async def compatibilidad(update: Update, context: ContextTypes.DEFAULT_TYPE): if len(context.args) < 2: await update.message.reply_text("💡 Uso: /compatibilidad @user1 @user2") return compat = random.randint(30, 100) await update.message.reply_text(f"🔗 Compatibilidad entre {context.args[0]} y {context.args[1]}: {compat}%")

🔝 Ranking menciones

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE): top = obtener_top_menciones()[:5] if not top: await update.message.reply_text("📉 No hay menciones aún.") return mensaje = "🏆 Ranking de menciones:\n" + "\n".join([f"{i+1}. @{u} - {c}" for i, (u, c) in enumerate(top)]) await update.message.reply_text(mensaje)

📣 Contador de menciones

async def contar_menciones(update: Update, context: ContextTypes.DEFAULT_TYPE): if update.message and update.message.entities: for entity in update.message.entities: if entity.type == "mention": username = update.message.text[entity.offset+1: entity.offset + entity.length] registrar_mencion(username)

🔁 Pareja automática cada hora

async def enviar_pareja_automatica(context: ContextTypes.DEFAULT_TYPE): global pareja_diaria pareja_diaria = obtener_pareja() if pareja_diaria: u1, u2 = pareja_diaria await context.bot.send_message(chat_id=GROUP_ID, text=f"💘 Pareja del día (automática): @{u1[1]} ❤️ @{u2[1]}")

====================================

Main

====================================

async def main(): app = ApplicationBuilder().token(TOKEN).build()

# Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("pareja", pareja))
app.add_handler(CommandHandler("nominacion", nominacion))
app.add_handler(CommandHandler("expulsion", expulsion))
app.add_handler(CommandHandler("compatibilidad", compatibilidad))
app.add_handler(CommandHandler("top", top))
app.add_handler(MessageHandler(filters.TEXT & filters.Entity("mention"), contar_menciones))

# JobQueue para pareja automática
app.job_queue.run_repeating(enviar_pareja_automatica, interval=3600, first=10)

print("Bot corriendo...")
await app.run_polling()

if name == "main": import asyncio asyncio.run(main())

