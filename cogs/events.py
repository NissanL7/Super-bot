import discord
from discord.ext import commands

class Events(commands.Cog):
    """Bot event listeners"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Runs when bot connects to Discord"""
        print(f"✅ Bot is online as {self.bot.user} (ID: {self.bot.user.id})")
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Welcome new members"""
        channel = member.guild.system_channel
        if channel:
            await channel.send(f"👋 Welcome {member.mention}! Type `!help` to get started!")

# This function tells discord.py how to load the cog
async def setup(bot):
    await bot.add_cog(Events(bot))
