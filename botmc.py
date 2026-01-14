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
        try:
            channel = await bot.fetch_channel(CHANNEL_ID)
        except Exception as e:
            print(f"[Monitor] No se pudo obtener el canal: {e}")
            channel = None

        status = await asyncio.to_thread(server.status)

        # Revisamos si la versión indica Offline
        if status.version.name.lower() == "§c● offline":
            mensaje_estado = "🔴 Servidor INACTIVO"
            actualmente_online = False
        else:
            mensaje_estado = "🟢 Servidor ONLINE"
            actualmente_online = True

        # Solo enviamos mensaje si cambia el estado
        if actualmente_online != server_online and channel:
            if actualmente_online:
                await channel.send(
                    f"🟢 **Servidor ENCENDIDO**\n"
                    f"📍 `{MC_SERVER}`\n"
                    f"👥 Jugadores conectados: {status.players.online}/{status.players.max}"
                )
            else:
                await channel.send(
                    f"🔴 **Servidor INACTIVO**\n"
                    f"📍 `{MC_SERVER}`"
                )
            server_online = actualmente_online

    except Exception as e:
        print(f"[Monitor] Error al consultar el servidor: {e}")

# =====================
# COMANDO !mc
# =====================
@bot.command()
async def mc(ctx):
    print(f"[Comando !mc] recibido en canal {ctx.channel.id}")
    server = get_server()

    try:
        status = await asyncio.to_thread(server.status)

        # Revisamos si la versión indica Offline
        if status.version.name.lower() == "§c● offline":
            mensaje_estado = "🔴 Servidor INACTIVO"
        else:
            mensaje_estado = "🟢 Servidor ONLINE"

        await ctx.send(
            f"{mensaje_estado}\n"
            f"📍 `{MC_SERVER}`\n"
            f"👥 Jugadores conectados: {status.players.online}/{status.players.max}\n"
            f"⏱ Latencia: {round(status.latency)}ms\n"
            f"⚙ Versión: {status.version.name}"
        )

    except Exception as e:
        print(f"[Comando !mc] Error al consultar el servidor: {e}")
        await ctx.send("🔴 Servidor OFFLINE")

# =====================
# INICIAR BOT
# =====================
bot.run(TOKEN)
