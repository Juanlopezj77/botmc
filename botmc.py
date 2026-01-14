import discord
from discord.ext import commands, tasks
from mcstatus import JavaServer
import asyncio

# ===== CONFIGURACIÓN =====
TOKEN = 'MTQ2MTA0NjU1NTE4NzYwOTY1Mg.GWBroS.rscKaCBU1uUMvhEe_-fVPWikHW6WRZ0OphYIfo'
CHANNEL_ID = 376783866398113792
MC_SERVER = 'Cobblemousler.exaroton.me:46834'
# =========================

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

servidor_estaba_on = None  # None = estado desconocido

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')
    monitorear.start()

@tasks.loop(minutes=2)
async def monitorear():
    global servidor_estaba_on
    canal = bot.get_channel(CHANNEL_ID)

    if canal is None:
        print("❌ No se encontró el canal")
        return

    try:
        server = JavaServer.lookup(MC_SERVER)
        status = await asyncio.to_thread(server.status)

        # Servidor ONLINE
        if servidor_estaba_on in (False, None):
            await canal.send(
                f"🟢 **¡Servidor ENCENDIDO!**\n"
                f"👥 Jugadores: **{status.players.online}/{status.players.max}**\n"
                f"📍 `{MC_SERVER}`"
            )

        servidor_estaba_on = True

    except Exception as e:
        # Servidor OFFLINE
        if servidor_estaba_on in (True, None):
            await canal.send("🔴 **Servidor APAGADO o no responde**")

        servidor_estaba_on = False
        print(f"Error al consultar el servidor: {e}")

@bot.command(name='mc')
async def check(ctx):
    """Verifica el estado del servidor"""
    try:
        server = JavaServer.lookup(MC_SERVER)
        status = await asyncio.to_thread(server.status)

        jugadores = ""
        if status.players.sample:
            jugadores = "\n🎮 " + ", ".join(p.name for p in status.players.sample)

        await ctx.send(
            f"🟢 **Servidor ONLINE**\n"
            f"👥 **{status.players.online}/{status.players.max}**"
            f"{jugadores}"
        )

    except:
        await ctx.send("🔴 **Servidor OFFLINE**")

bot.run(TOKEN)
