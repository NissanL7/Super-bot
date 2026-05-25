import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

bot.run(os.getenv("DISCORD_TOKEN"))
