import os
import discord
from discord.ext import commands, tasks
from mcstatus import JavaServer
from dotenv import load_dotenv

# =====================
# CARGAR VARIABLES
# =====================
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
MC_SERVER = os.getenv("MC_SERVER")  # ip:puerto

# =====================
# MINECRAFT SERVER
# =====================
def get_server():
    if ":" in MC_SERVER:
        host, port = MC_SERVER.split(":")
        return JavaServer(host, int(port))
    return JavaServer(MC_SERVER, 25565)

# =====================
# DISCORD CONFIG
# =====================
intents = discord.Intents.default()
intents.message_content = True  # 🔴 OBLIGATORIO PARA !mc

bot = commands.Bot(command_prefix="!", intents=intents)

server_online = False  # estado anterior

# =====================
# BOT READY
# =====================
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    monitor.start()

# =====================
# MONITOREO AUTOMÁTICO
# =====================
@tasks.loop(minutes=1)
async def monitor():
    global server_online
    channel = bot.get_channel(CHANNEL_ID)

    try:
        server = get_server()
        server.query()  # SOLO responde cuando ya deja entrar

        if not server_online:
            await channel.send(
                f"🟢 **Servidor ENCENDIDO**\n"
                f"📍 `{MC_SERVER}`"
            )
            server_online = True

    except Exception:
        if server_online:
            await channel.send(
                f"🔴 **Servidor APAGADO**\n"
                f"📍 `{MC_SERVER}`"
            )
            server_online = False

# =====================
# COMANDO !mc
# =====================
@bot.command()
async def mc(ctx):
    if ctx.channel.id != CHANNEL_ID:
        return  # solo responde en este canal

    try:
        server = get_server()
        query = server.query()

        await ctx.send(
            f"🟢 **Servidor ONLINE**\n"
            f"📍 `{MC_SERVER}`\n"
            f"👥 Jugadores: {len(query.players.names)}/{query.players.max}"
        )

    except Exception:
        await ctx.send("🔴 **Servidor OFFLINE**")

# =====================
# START BOT
# =====================
bot.run(TOKEN)
