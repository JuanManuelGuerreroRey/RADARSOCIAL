import logging import os import json import random from telegram import Update from telegram.ext import ( ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters ) from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = "8027791367:AAHOlycqUkBdVdM88dVBaIRr57piN3DRXR4" GROUP_ID = -1001169225264

interactions_file = "interacciones.json"

logging.basicConfig( format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO )

pareja_diaria = None nominados = [] menciones = {}

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

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text( "/start - Iniciar bot\n" "/pareja - Mostrar pareja del día\n" "/nominacion - Nominar a alguien (modo reality)\n" "/expulsion - Expulsar a alguien\n" "/compatibilidad - Ver compatibilidad\n" "/menciones - Ver ranking de menciones\n" "/help - Ver comandos disponibles" )

async def pareja(update: Update, context: ContextTypes.DEFAULT_TYPE): global pareja_diaria if not pareja_diaria: pareja_diaria = obtener_pareja() if pareja_diaria: u1, u2 = pareja_diaria await update.message.reply_text(f"💞 Pareja del día: @{u1[1]} y @{u2[1]}") else: await update.message.reply_text("❗ No hay suficientes usuarios para emparejar.")

async def nominacion(update: Update, context: ContextTypes.DEFAULT_TYPE): if not context.args: await update.message.reply_text("🔁 Especifica a quién nominas. Ej: /nominacion @usuario") return nominado = context.args[0] nominados.append(nominado) await update.message.reply_text(f"📣 Has nominado a {nominado}.")

async def expulsion(update: Update, context: ContextTypes.DEFAULT_TYPE): if not context.args: await update.message.reply_text("🔁 Especifica a quién expulsas. Ej: /expulsion @usuario") return expulsado = context.args[0] if expulsado in nominados: nominados.remove(expulsado) await update.message.reply_text(f"🛑 {expulsado} ha sido expulsado.") else: await update.message.reply_text(f"❌ {expulsado} no estaba nominado.")

async def compatibilidad(update: Update, context: ContextTypes.DEFAULT_TYPE): if len(context.args) < 2: await update.message.reply_text("💡 Uso: /compatibilidad @user1 @user2") return compat = random.randint(30, 100) await update.message.reply_text(f"🔗 Compatibilidad entre {context.args[0]} y {context.args[1]}: {compat}%")

async def contar_menciones(update: Update, context: ContextTypes.DEFAULT_TYPE): texto = update.message.text for entidad in update.message.entities: if entidad.type == 'mention': mencionado = texto[entidad.offset:entidad.offset + entidad.length] menciones[mencionado] = menciones.get(mencionado, 0) + 1

async def ranking_menciones(update: Update, context: ContextTypes.DEFAULT_TYPE): if not menciones: await update.message.reply_text("📉 Aún no hay menciones registradas.") return ranking = sorted(menciones.items(), key=lambda x: x[1], reverse=True) texto = "🏆 Ranking de menciones:\n" + "\n".join([f"{m[0]}: {m[1]}" for m in ranking]) await update.message.reply_text(texto)

async def enviar_pareja_automatica(context: ContextTypes.DEFAULT_TYPE): global pareja_diaria pareja_diaria = obtener_pareja() if pareja_diaria: u1, u2 = pareja_diaria await context.bot.send_message(chat_id=GROUP_ID, text=f"💞 Pareja del día (automática): @{u1[1]} y @{u2[1]}")

====================================

Main

====================================

async def main(): app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("pareja", pareja))
app.add_handler(CommandHandler("nominacion", nominacion))
app.add_handler(CommandHandler("expulsion", expulsion))
app.add_handler(CommandHandler("compatibilidad", compatibilidad))
app.add_handler(CommandHandler("menciones", ranking_menciones))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, contar_menciones))

scheduler = AsyncIOScheduler()
scheduler.add_job(enviar_pareja_automatica, 'interval', hours=1, args=[app.bot])
scheduler.start()

print("Bot corriendo...")
await app.run_polling()

if name == "main": import asyncio asyncio.run(main())

                                           
