import os
import discord
from discord.ext import commands, tasks
from mcstatus import JavaServer
import asyncio

# ===== CONFIGURACIÓN DESDE VARIABLES DE ENTORNO =====
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
MC_SERVER = os.getenv("MC_SERVER")
# ===================================================

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

servidor_estaba_on = False

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')
    monitorear.start()

@tasks.loop(minutes=2)
async def monitorear():
    global servidor_estaba_on

    try:
        server = JavaServer.lookup(MC_SERVER)
        status = await asyncio.to_thread(server.status)

        if not servidor_estaba_on:
            canal = bot.get_channel(CHANNEL_ID)
            if canal:
                await canal.send(
                    f"🟢 **¡Servidor encendido!**\n"
                    f"👥 Jugadores: **{status.players.online}/{status.players.max}**\n"
                    f"📍 Dirección: `{MC_SERVER}`"
                )
            servidor_estaba_on = True

    except Exception as e:
        servidor_estaba_on = False
        print(f"Servidor offline o error: {e}")

@bot.command(name='mc')
async def check(ctx):
    """Verifica si el servidor está online"""
    try:
        server = JavaServer.lookup(MC_SERVER)
        status = await asyncio.to_thread(server.status)

        jugadores_lista = ""
        if status.players.sample:
            jugadores_lista = "\n🎮 " + ", ".join([p.name for p in status.players.sample])

        await ctx.send(
            f"🟢 **Servidor ONLINE**\n"
            f"👥 Jugadores: **{status.players.online}/{status.players.max}**"
            f"{jugadores_lista}"
        )

    except:
        await ctx.send("🔴 **Servidor OFFLINE** (apagado o no responde)")

# ===== VALIDACIÓN DE VARIABLES =====
if not TOKEN or not CHANNEL_ID or not MC_SERVER:
    raise ValueError("❌ Faltan variables de entorno. Revisa DISCORD_TOKEN, CHANNEL_ID y MC_SERVER.")

bot.run(TOKEN)
