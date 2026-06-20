import discord
import os
import random
from threading import Thread
from flask import Flask
from discord.ext import commands

# ==========================================
# MANTENER VIVO (Web Server)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Supervisor-kun está en línea y vigilando. 🤖"

def run():
    # Usamos el puerto que Railway asigna automáticamente
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# ==========================================
# CONFIGURACIÓN DE IDS Y BOT
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
        print(f"⚠️  No se encontró {ruta}. Usando lista vacía.")
    return palabras

PALABRAS_PROHIBIDAS = cargar_palabras_prohibidas()
print(f"📋 {len(PALABRAS_PROHIBIDAS)} palabras prohibidas cargadas.")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==========================================
# EVENTOS Y COMANDOS (Tu código original se mantiene intacto aquí)
# ==========================================
@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} se ha encendido con éxito.')
    await bot.change_presence(activity=discord.Game(name="Supervisar Torneos | !ayuda"))

# ... (El resto de tus eventos y comandos van aquí, el código que ya tenías está bien) ...

# ==========================================
# ENCENDIDO
# ==========================================
if __name__ == "__main__":
    keep_alive()
    TOKEN = os.environ.get('DISCORD_TOKEN')
    if not TOKEN:
        raise ValueError("❌ DISCORD_TOKEN no está configurado en las variables de entorno.")
    bot.run(TOKEN)
