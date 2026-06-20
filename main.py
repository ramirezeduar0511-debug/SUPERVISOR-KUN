import discord
import os
import random
from threading import Thread
from flask import Flask
from discord.ext import commands

# ==========================================
# KEEP-ALIVE
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Supervisor-kun está en línea y vigilando. 🤖"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# ==========================================
# CONFIGURACIÓN
# ==========================================
ID_REGLAS = 1517599043612577975
ID_BIENVENIDA = 1517522103761502321
ID_ANUNCIOS = 1517523081164488734
ID_ZONA_COMBATE = 1517620280862707802

def cargar_palabras_prohibidas():
    ruta = os.path.join(os.path.dirname(__file__), "palabras_prohibidas.txt")
    palabras = []
    try:
        with open(ruta, encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if linea and not linea.startswith("#"):
                    palabras.append(linea.lower())
    except FileNotFoundError:
        pass
    return palabras

PALABRAS_PROHIBIDAS = cargar_palabras_prohibidas()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==========================================
# EVENTOS
# ==========================================
@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} conectado.')
    await bot.change_presence(activity=discord.Game(name="Supervisar Torneos | !ayuda"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Filtro
    contenido = message.content.lower()
    if any(p in contenido for p in PALABRAS_PROHIBIDAS):
        await message.delete()
        return

    # ESTA LÍNEA ES CLAVE: Permite que el bot procese los comandos
    await bot.process_commands(message)

# ==========================================
# COMANDOS (Incluye los tuyos aquí abajo)
# ==========================================
@bot.command()
async def ayuda(ctx):
    await ctx.send("Comandos disponibles: !anuncio, !creadores, !limpiar, !dados, !moneda, !vs")

@bot.command()
async def creadores(ctx):
    await ctx.send("👑 Darkoni / Jugo de Rey: Twitch, TikTok, YouTube.")

# ... (Añade aquí el resto de tus comandos: !anuncio, !limpiar, etc.)

# ==========================================
# ENCENDIDO
# ==========================================
if __name__ == "__main__":
    keep_alive()
    TOKEN = os.environ.get('DISCORD_TOKEN')
    if not TOKEN:
        raise ValueError("❌ DISCORD_TOKEN no configurado en Railway.")
    bot.run(TOKEN)
