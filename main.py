import os
import discord
from discord.ext import commands

# Debug: Print what we're reading
print(f"🔍 DISCORD_TOKEN value: {os.getenv('DISCORD_TOKEN')[:10] if os.getenv('DISCORD_TOKEN') else 'NOT SET'}...")

if not os.getenv("DISCORD_TOKEN"):
    print("❌ FATAL: Token not found!")
    exit(1)

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"✅ SUCCESS: {bot.user} is online!")

bot.run(os.getenv("DISCORD_TOKEN"))
