from flask import Flask
from threading import Thread
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# Keep alive server
app = Flask(__name__)

@app.route('/')
def home():
    return "Super Bot is online! 🤖"

def run_server():
    app.run(host='0.0.0.0', port=8080)
# Debug: Print what we're reading
print(f"🔍 DISCORD_TOKEN value: {os.getenv('DISCORD_TOKEN')[:10] if os.getenv('DISCORD_TOKEN') else 'NOT SET'}...")

# Start web server in background
Thread(target=run_server).start()
if not os.getenv("DISCORD_TOKEN"):
    print("❌ FATAL: Token not found!")
    exit(1)

# Your bot code
load_dotenv()
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")
    print(f"✅ SUCCESS: {bot.user} is online!")

bot.run(os.getenv("DISCORD_TOKEN"))
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="🤖 Super Bot Help",
        description="Here's how to use me!",
        color=discord.Color.blue()
    )
    embed.add_field(name="🏓 !ping", value="Check if I'm online", inline=False)
    embed.add_field(name="📊 !rank", value="See your XP level", inline=False)
    embed.add_field(name="🆘 !help", value="Show this help message", inline=False)
    embed.set_footer(text="Made with ❤️ by YourName")
    await ctx.send(embed=embed)
