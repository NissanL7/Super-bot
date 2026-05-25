from flask import Flask
from threading import Thread
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

# Start web server in background
Thread(target=run_server).start()

# Your bot code
load_dotenv()
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

bot.run(os.getenv("DISCORD_TOKEN"))
