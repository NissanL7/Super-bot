import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

class HighTech(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="chat", description="Chat with the AI brain")
    @app_commands.describe(prompt="What do you want to ask the AI?")
    async def chat(self, interaction: discord.Interaction, prompt: str):
        await interaction.response.defer()
        
        if not HF_TOKEN:
            return await interaction.followup.send("❌ HF_TOKEN is missing in environment variables!", ephemeral=True)

        API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        
        formatted_prompt = f"<s>[INST] {prompt} [/INST]"
        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(API_URL, headers=headers, json=payload) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        ai_reply = result[0]['generated_text'].strip()
                        
                        embed = discord.Embed(
                            title="🧠 AI Response", 
                            description=ai_reply[:4000] if ai_reply else "No response generated",
                            color=0x9b59b6
                        )
                        embed.set_footer(text="Powered by Hugging Face - Mistral 7B")
                        await interaction.followup.send(embed=embed)                    else:
                        error_text = await resp.text()
                        await interaction.followup.send(f"❌ AI API Error: {resp.status}", ephemeral=True)
                        print(f"HF API Error: {error_text}")
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)

    @app_commands.command(name="study", description="Start a 25-minute focus timer for Maths/Physics/Chemistry")
    async def study(self, interaction: discord.Interaction):
        view = StudyView(interaction.user)
        embed = discord.Embed(title="🍅 Pomodoro Study Timer", description="Click **Start** to focus for 25 minutes!", color=0xe74c3c)
        embed.add_field(name="Focus Subjects", value="📐 Maths | ⚛️ Physics | 🧪 Chemistry", inline=False)
        await interaction.response.send_message(embed=embed, view=view)

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
        
        interaction.client.loop.create_task(self.run_timer(interaction))

    async def run_timer(self, interaction: discord.Interaction):
        await asyncio.sleep(1500) 
        embed = discord.Embed(title="⏰ Time's Up!", description=f"Great job {self.user.mention}! Take a 5-minute break.", color=0x2ecc71)        await interaction.followup.send(embed=embed)
        self.is_running = False

async def setup(bot):
    await bot.add_cog(HighTech(bot))
