import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar .env explícitamente desde la carpeta del script
env_path = Path(__file__).parent / ".env"
print("ENV FILE PATH:", env_path)
print("ENV EXISTS:", env_path.exists())

load_dotenv(dotenv_path=env_path)

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
MC_SERVER = os.getenv("MC_SERVER")

print("TOKEN LOADED:", bool(TOKEN))
print("CHANNEL_ID RAW:", CHANNEL_ID)
print("MC_SERVER:", MC_SERVER)

if not TOKEN:
    raise ValueError("❌ DISCORD_TOKEN no cargado")
if not CHANNEL_ID:
    raise ValueError("❌ CHANNEL_ID no cargado")
if not MC_SERVER:
    raise ValueError("❌ MC_SERVER no cargado")

CHANNEL_ID = int(CHANNEL_ID)
