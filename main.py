import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from flask import Flask
from threading import Thread

# ============ KEEP-ALIVE SERVER (for Render) ============
app = Flask(__name__)

@app.route('/')
def home():
    return "Super Bot is online! 🤖"

@app.route('/health')
def health():
    return {"status": "ok"}, 200

def run_server():
    app.run(host='0.0.0.0', port=8080)

# Start Flask in background thread
Thread(target=run_server, daemon=True).start()
# ========================================================

# ============ BOT SETUP ============
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ ERROR: DISCORD_TOKEN not found!")
    exit(1)
else:
    print(f"✅ Token loaded (length: {len(TOKEN)})")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ============ LOAD COGS ============
async def load_cogs():
    """Load all cogs from the cogs/ folder"""
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            cog_name = filename[:-3]  # Remove .py
            try:
                await bot.load_extension(f"cogs.{cog_name}")
                print(f"📦 Loaded cog: {cog_name}")
            except Exception as e:
                print(f"❌ Failed to load {cog_name}: {e}")

# ============ RUN BOT ============
async def main():
    await load_cogs()
    await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
