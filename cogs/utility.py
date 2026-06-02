import discord
from discord.ext import commands
import time

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    @commands.command()
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! Latency: {latency}ms")

    @commands.command()
    async def help_cmd(self, ctx):
        embed = discord.Embed(title="📜 Super Bot Help", color=0x3498db)
        embed.add_field(name="🎮 Leveling", value="`!rank`, `!leaderboard`", inline=False)
        embed.add_field(name="⚙️ Utility", value="`!ping`, `!stats`", inline=False)
        embed.set_footer(text="Prefix is !")
        await ctx.send(embed=embed)

    @commands.command()
    async def stats(self, ctx):
        """Show bot statistics"""
        uptime = int(time.time() - self.start_time)
        embed = discord.Embed(title="🤖 Super Bot Stats", color=0x3498db)
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Users", value=sum(g.member_count for g in self.bot.guilds if g.member_count), inline=True)
        embed.add_field(name="Commands", value=len(self.bot.commands), inline=True)
        embed.add_field(name="Uptime", value=f"{uptime // 3600}h {(uptime % 3600) // 60}m", inline=True)
        embed.set_footer(text="Made with ❤️")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
