import discord
from discord.ext import commands

class Utility(commands.Cog):
    """Basic utility commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def ping(self, ctx):
        """Check if bot is online"""
        await ctx.send("🏓 Pong!")
    
    @commands.command()
    async def help(self, ctx):
        """Show help menu"""
        embed = discord.Embed(
            title="🤖 Super Bot Help",
            description="Here's how to use me!",
            color=discord.Color.blue()
        )
        embed.add_field(name="🏓 !ping", value="Check if I'm online", inline=False)
        embed.add_field(name="📊 !rank", value="See your XP level (coming soon!)", inline=False)
        embed.add_field(name="🆘 !help", value="Show this help message", inline=False)
        embed.set_footer(text="Made with ❤️")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
