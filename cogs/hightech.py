import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
# We will set this up in the next step
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class HighTech(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- FEATURE 1: AI CHATBOT (Powered by Google Gemini) ---
    @app_commands.command(name="chat", description="Chat with the bot's AI brain")
    @app_commands.describe(prompt="What do you want to ask the AI?")
    async def chat(self, interaction: discord.Interaction, prompt: str):
        await interaction.response.defer() # AI takes a few seconds, so we tell Discord to wait
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    try:
                        ai_reply = data['candidates'][0]['content']['parts'][0]['text']
                    except (KeyError, IndexError):
                        ai_reply = "I couldn't process that request."
                    
                    embed = discord.Embed(title="🧠 AI Response", description=ai_reply[:4000], color=0x9b59b6)
                    embed.set_footer(text="Powered by Google Gemini")
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("❌ AI is unavailable. Check your API key!", ephemeral=True)

    # --- FEATURE 2: INTERACTIVE POMODORO TIMER (For your Board Exams!) ---
    @app_commands.command(name="study", description="Start a 25-minute focus timer for Maths/Physics/Chemistry")
    async def study(self, interaction: discord.Interaction):
        view = StudyView(interaction.user)
        embed = discord.Embed(title="🍅 Pomodoro Study Timer", description="Click **Start** to focus for 25 minutes!", color=0xe74c3c)
        embed.add_field(name="Focus Subjects", value="📐 Maths | ⚛️ Physics | 🧪 Chemistry", inline=False)
        await interaction.response.send_message(embed=embed, view=view)

    # --- FEATURE 3: RANDOM MEME GENERATOR ---
    @app_commands.command(name="meme", description="Get a random high-quality meme")
    async def meme(self, interaction: discord.Interaction):
        await interaction.response.defer()
        async with aiohttp.ClientSession() as session:
            async with session.get("https://meme-api.com/gimme") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    embed = discord.Embed(title=data['title'], url=data['postLink'], color=0xf39c12)
                    embed.set_image(url=data['url'])
                    embed.set_footer(text=f"👍 {data['ups']} | r/{data['subreddit']}")
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("❌ Couldn't fetch a meme right now.")

class StudyView(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=None)
        self.user = user
        self.is_running = False

    @discord.ui.button(label="Start 25m Timer", style=discord.ButtonStyle.success, emoji="▶️")
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            return await interaction.response.send_message("This isn't your timer!", ephemeral=True)
        if self.is_running:
            return await interaction.response.send_message("Timer already running!", ephemeral=True)

        self.is_running = True
        button.disabled = True
        await interaction.response.edit_message(view=self)
        
        # Run timer in the background so it doesn't freeze the bot
        interaction.client.loop.create_task(self.run_timer(interaction))

    async def run_timer(self, interaction: discord.Interaction):
        # 25 minutes = 1500 seconds. (Change to 10 seconds if you want to test it quickly!)
        await asyncio.sleep(1500) 
        embed = discord.Embed(title="⏰ Time's Up!", description=f"Great job {self.user.mention}! Take a 5-minute break.", color=0x2ecc71)
        await interaction.followup.send(embed=embed)
        self.is_running = False

async def setup(bot):
    await bot.add_cog(HighTech(bot))
