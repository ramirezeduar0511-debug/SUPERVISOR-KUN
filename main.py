import discord
import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Supervisor-kun está en línea y vigilando. 🤖"

def run():
    # Railway inyecta el puerto en la variable de entorno 'PORT'
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


# ==========================================
# KEEP-ALIVE (web server for uptime monitoring)
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "Supervisor-kun está en línea y vigilando. 🤖"

def run():
    app.run(host='0.0.0.0', port=8080)

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
    """Carga las palabras prohibidas desde bot/palabras_prohibidas.txt.
    Ignora líneas vacías y comentarios (#). Recargable en caliente."""
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
# EVENTOS
# ==========================================
@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} se ha encendido con éxito.')
    await bot.change_presence(activity=discord.Game(name="Supervisar Torneos | !ayuda"))

@bot.event
async def on_member_join(member):
    canal = bot.get_channel(ID_BIENVENIDA)
    if canal:
        embed = discord.Embed(
            title=f"👋 ¡Bienvenido/a a la comunidad, {member.name}!",
            description="¡Un nuevo miembro se ha unido al servidor! Pásatela genial y recuerda revisar las reglas.",
            color=discord.Color.dark_purple()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await canal.send(
            content=f"🔔 ¡Atención @everyone, denle la bienvenida a {member.mention}! 🎉",
            embed=embed
        )

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    contenido = message.content.lower()
    tiene_palabra_prohibida = any(palabra in contenido for palabra in PALABRAS_PROHIBIDAS)
    tiene_link_prohibido = "http" in contenido and any(p in contenido for p in ["porno", "xxx", "hentai", "sex"])

    if tiene_palabra_prohibida or tiene_link_prohibido:
        try:
            await message.delete()
            await message.author.send(
                f"⚠️ Hola {message.author.name}, tu mensaje en **{message.guild.name}** fue eliminado por "
                f"Supervisor-kun debido a que contenía vocabulario explícito o links prohibidos. Mantengamos el respeto."
            )
        except Exception:
            pass
        return

    await bot.process_commands(message)

# ==========================================
# ANUNCIOS
# ==========================================
@bot.command()
@commands.has_permissions(administrator=True)
async def anuncio(ctx, link: str, *, texto: str):
    """Publica un anuncio estético con link de Stream."""
    await ctx.message.delete()
    canal = bot.get_channel(ID_ANUNCIOS)
    if canal:
        embed = discord.Embed(title="🔥 ¡ANUNCIO IMPORTANTE! 🔥", description=texto, color=discord.Color.red())
        embed.add_field(name="🌐 Directo / Publicación:", value=link, inline=False)
        embed.set_footer(text="Transmisión supervisada por Supervisor-kun")
        await canal.send(content="@everyone 📢 ¡Hay novedades importantes!", embed=embed)

@bot.command()
async def creadores(ctx):
    """Muestra las redes sociales de los creadores."""
    embed = discord.Embed(
        title="🎬 Creadores de Contenido Oficiales",
        description="¡Sigue a nuestro equipo en sus plataformas de streaming y redes!",
        color=discord.Color.gold()
    )
    embed.add_field(
        name="👑 Darkoni / Jugo de Rey",
        value="• [Twitch](https://twitch.tv)\n• [TikTok](https://tiktok.com)\n• [YouTube](https://youtube.com)",
        inline=False
    )
    await ctx.send(embed=embed)

# ==========================================
# REGLAS
# ==========================================
@bot.command()
@commands.has_permissions(administrator=True)
async def reglas_server(ctx, *, texto: str):
    """Publica las reglas del servidor."""
    await ctx.message.delete()
    canal = bot.get_channel(ID_REGLAS)
    if canal:
        embed = discord.Embed(
            title="📜 REGLAS GENERALES DEL SERVIDOR",
            description=texto,
            color=discord.Color.dark_gray()
        )
        await canal.send(content="@everyone Por favor, lean atentamente las normas de convivencia.", embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def torneo_reglas(ctx, *, texto: str):
    """Publica las reglas del torneo."""
    await ctx.message.delete()
    canal = bot.get_channel(ID_REGLAS)
    if canal:
        embed = discord.Embed(
            title="🏆 REGLAS DEL TORNEO ACTIVO",
            description=texto,
            color=discord.Color.orange()
        )
        await canal.send(
            content="@everyone ⚔️ ¡Normativas oficiales para el torneo actual! Cumplir estrictamente.",
            embed=embed
        )

# ==========================================
# ZONA DE COMBATE
# ==========================================
@bot.command()
@commands.has_permissions(manage_channels=True)
async def crear_equipos(ctx, num_salas: int, limite: int, prefijo: str):
    """Crea múltiples salas de voz para equipos. Uso: !crear_equipos 4 5 Equipo"""
    categoria = bot.get_channel(ID_ZONA_COMBATE)
    if isinstance(categoria, discord.CategoryChannel):
        await ctx.send(f"⏳ Supervisor-kun está creando {num_salas} salas de voz...")
        for i in range(1, num_salas + 1):
            await ctx.guild.create_voice_channel(
                name=f"{prefijo} {i}",
                category=categoria,
                user_limit=limite
            )
        await ctx.send("✅ ¡Salas de equipos creadas con éxito!")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def crear_sala(ctx, nombre: str, limite: int):
    """Crea una sala de voz personalizada. Uso: !crear_sala NombreSala 5"""
    categoria = bot.get_channel(ID_ZONA_COMBATE)
    if isinstance(categoria, discord.CategoryChannel):
        await ctx.guild.create_voice_channel(name=nombre, category=categoria, user_limit=limite)
        await ctx.send(f"✅ Sala de voz `{nombre}` creada correctamente.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def borrar_salas(ctx):
    """Elimina todas las salas de voz de la Zona de Combate."""
    categoria = bot.get_channel(ID_ZONA_COMBATE)
    if isinstance(categoria, discord.CategoryChannel):
        await ctx.send("🧹 Limpiando los canales de la Zona de Combate...")
        for canal in categoria.voice_channels:
            await canal.delete()
        await ctx.send("✅ Todos los canales de voz han sido removidos.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def ocultar_salas(ctx):
    """Alterna la visibilidad de la Zona de Combate."""
    categoria = bot.get_channel(ID_ZONA_COMBATE)
    if isinstance(categoria, discord.CategoryChannel):
        rol_everyone = ctx.guild.default_role
        permisos_actuales = categoria.overwrites_for(rol_everyone)

        if permisos_actuales.view_channel is False:
            permisos_actuales.view_channel = None
            await categoria.set_permissions(rol_everyone, overwrite=permisos_actuales)
            await ctx.send("👁️ La Zona de Combate ahora es **Visible** para todos.")
        else:
            permisos_actuales.view_channel = False
            await categoria.set_permissions(rol_everyone, overwrite=permisos_actuales)
            await ctx.send("🔒 La Zona de Combate ahora está **Oculta** para miembros comunes.")

# ==========================================
# MODERACIÓN
# ==========================================
@bot.command()
@commands.has_permissions(administrator=True)
async def recargar_filtro(ctx):
    """Recarga la lista de palabras prohibidas desde el archivo sin reiniciar el bot."""
    global PALABRAS_PROHIBIDAS
    PALABRAS_PROHIBIDAS = cargar_palabras_prohibidas()
    await ctx.send(f"✅ Filtro recargado. **{len(PALABRAS_PROHIBIDAS)} palabras** prohibidas activas.")


@bot.command()
@commands.has_permissions(manage_messages=True)
async def limpiar(ctx, cantidad: int):
    """Limpia mensajes del canal. Uso: !limpiar 10"""
    await ctx.channel.purge(limit=cantidad + 1)
    msg = await ctx.send(f"🧹 Chat limpiado por orden de Supervisor-kun ({cantidad} mensajes).")
    await msg.delete(delay=4)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, motivo="No especificado"):
    """Banea a un miembro. Uso: !ban @usuario motivo"""
    await member.ban(reason=motivo)
    await ctx.send(f"🔨 {member.name} ha sido baneado permanentemente. Motivo: {motivo}")

# ==========================================
# ENTRETENIMIENTO
# ==========================================
@bot.command()
async def dados(ctx):
    """Lanza un dado del 1 al 6."""
    resultado = random.randint(1, 6)
    await ctx.send(f"🎲 {ctx.author.mention} lanzó un dado y sacó: **{resultado}**")

@bot.command()
async def moneda(ctx):
    """Lanza una moneda (Cara o Cruz)."""
    resultado = random.choice(["Cara", "Cruz"])
    await ctx.send(f"🪙 La moneda gira en el aire y cae en... **{resultado}**")

@bot.command()
async def vs(ctx, *, equipos: str):
    """Genera emparejamientos aleatorios. Uso: !vs TeamA, TeamB, TeamC"""
    lista = [e.strip() for e in equipos.split(",")]
    if len(lista) < 2:
        return await ctx.send(
            "❌ Debes colocar al menos 2 equipos separados por comas. Ejemplo: `!vs TeamA, TeamB, TeamC`"
        )

    random.shuffle(lista)
    emparejamientos = []
    while len(lista) > 1:
        e1 = lista.pop(0)
        e2 = lista.pop(0)
        emparejamientos.append(f"⚔️ **{e1}** VS **{e2}**")

    if lista:
        emparejamientos.append(f"⏳ **{lista[0]}** pasa directo a la siguiente ronda (Descansa).")

    embed = discord.Embed(
        title="📊 EMPAREJAMIENTOS GENERADOS POR SUPERVISOR-KUN",
        description="\n".join(emparejamientos),
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

# ==========================================
# ENCENDIDO
# ==========================================
if __name__ == "__main__":
    keep_alive()
    TOKEN = os.environ.get('DISCORD_TOKEN')
    if not TOKEN:
        raise ValueError("❌ DISCORD_TOKEN no está configurado en las variables de entorno.")
    bot.run(TOKEN)
