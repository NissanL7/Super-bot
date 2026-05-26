import discord
from discord.ext import commands

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"✅ Bot is online as {self.bot.user}")
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel:
            await channel.send(f"👋 Welcome {member.mention}! Type `!help` to get started!")

async def setup(bot):
    await bot.add_cog(Events(bot))
