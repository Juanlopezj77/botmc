import os
import discord
from discord.ext import commands, tasks
from mcstatus import JavaServer
from dotenv import load_dotenv
import asyncio
import socket

# =====================
# CARGAR VARIABLES
# =====================
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
MC_SERVER = os.getenv("MC_SERVER")  # ip:puerto

# Timeout global para evitar que mcstatus se quede colgado
socket.setdefaulttimeout(10)  # 10 segundos

# =====================
# SERVIDOR MINECRAFT
# =====================
def get_server():
    if ":" in MC_SERVER:
        host, port = MC_SERVER.split(":")
        return JavaServer(host, int(port))
    return JavaServer(MC_SERVER, 25565)

# =====================
# CONFIG DISCORD
# =====================
intents = discord.Intents.default()
intents.message_content = True

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
    server = get_server()

    try:
        # Obtenemos el canal desde la API, nunca será None
        channel = await bot.fetch_channel(CHANNEL_ID)

        status = await asyncio.to_thread(server.status)

        if not server_online:
            await channel.send(
                f"🟢 **Servidor ENCENDIDO**\n"
                f"📍 `{MC_SERVER}`\n"
                f"👥 Jugadores conectados: {status.players.online}/{status.players.max}"
            )
            server_online = True

    except Exception as e:
        # Si el servidor estaba online, avisamos que se apagó
        if server_online and 'channel' in locals() and channel is not None:
            await channel.send(
                f"🔴 **Servidor APAGADO**\n"
                f"📍 `{MC_SERVER}`"
            )
            server_online = False
        # Solo loguea el error en consola
        print(f"[Monitor] Error al consultar el servidor: {e}")

# =====================
# COMANDO !mc
# =====================
@bot.command()
async def mc(ctx):
    # Debug: saber que el comando fue recibido
    print(f"[Comando !mc] recibido en canal {ctx.channel.id}")
    server = get_server()

    try:
        status = await asyncio.to_thread(server.status)
        await ctx.send(
            f"🟢 **Servidor ONLINE**\n"
            f"📍 `{MC_SERVER}`\n"
            f"👥 Jugadores conectados: {status.players.online}/{status.players.max}\n"
            f"⏱ Latencia: {round(status.latency)}ms\n"
            f"⚙ Versión: {status.version.name}"
        )
    except Exception as e:
        # Solo loguea en consola, no en Discord
        print(f"[Comando !mc] Error al consultar el servidor: {e}")
        await ctx.send("🔴 **Servidor OFFLINE**")

# =====================
# INICIAR BOT
# =====================
bot.run(TOKEN)
