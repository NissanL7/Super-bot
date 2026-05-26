import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# ============ FLASK KEEP-ALIVE (for Render) ============
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Super Bot is running!"

@app.route('/health')
def health():
    return {"status": "ok"}, 200

def run_flask():
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 8080)))

# Start Flask in background
flask_thread = Thread(target=run_flask, daemon=True)
flask_thread.start()
# =======================================================

# ============ DISCORD BOT SETUP ============
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print("❌ FATAL: DISCORD_TOKEN not found in environment!")
    exit(1)

print(f"✅ Token found (length: {len(TOKEN)})")

# Enable all intents (required for members, messages, etc.)
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ============ COG LOADER ============
async def load_cogs():
    cog_folder = "cogs"
    if not os.path.exists(cog_folder):
        print(f"❌ Folder '{cog_folder}' not found!")
        return
    
    for filename in os.listdir(cog_folder):
        if filename.endswith(".py") and not filename.startswith("__"):
            cog_name = filename[:-3]
            try:
                await bot.load_extension(f"{cog_folder}.{cog_name}")
                print(f"✅ Loaded cog: {cog_name}")
            except Exception as e:
                print(f"❌ Failed to load {cog_name}: {e}")

# ============ BOT EVENTS ============
@bot.event
async def on_ready():
    print(f"🟢 SUCCESS! {bot.user} is online and connected to Discord!")
    print(f"   → In {len(bot.guilds)} server(s)")
    print(f"   → Ready to respond to commands!")

# ============ STARTUP ============
async def main():
    await load_cogs()
    print("🔑 Starting Discord connection...")
    await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👋 Bot shutting down...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
