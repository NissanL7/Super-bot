import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Optional: Uncomment the next two lines if you are using a keep-alive server (Render/Replit)
# from keep_alive import keep_alive

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Best practice: Only request the intents you actually need
intents = discord.Intents.default()
intents.message_content = True  # Required for reading message content (XP, commands)
intents.members = True          # Required for leaderboards and member joins

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user.name} ({bot.user.id})")
    print(f"🌐 Connected to {len(bot.guilds)} servers")

async def load_cogs():
    for filename in os.listdir("./cogs"):
        # Ignore __init__.py so it doesn't try to load it as a cog
        if filename.endswith(".py") and filename != "__init__.py":
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"✅ Loaded cog: {filename}")

@bot.event
async def setup_hook():
    await load_cogs()

if __name__ == "__main__":
    # keep_alive() # Uncomment if using keep_alive.py
    bot.run(TOKEN)
    import threading
# ... other imports
from keep_alive import run_server
