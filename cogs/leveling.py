import discord
from discord.ext import commands, tasks
import json
import os
import random

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.xp_file = "xp_data.json"
        self.xp_data = self.load_xp()
        self.auto_save_xp.start()

    def cog_unload(self):
        self.auto_save_xp.cancel()
        self.save_xp()

    def load_xp(self):
        if os.path.exists(self.xp_file):
            with open(self.xp_file, "r") as f:
                return json.load(f)
        return {}

    def save_xp(self):
        with open(self.xp_file, "w") as f:
            json.dump(self.xp_data, f, indent=4)

    @tasks.loop(minutes=5)
    async def auto_save_xp(self):
        self.save_xp()

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore bots and DMs
        if message.author.bot or not message.guild:
            return

        # Key XP by server AND user
        key = f"{message.guild.id}_{message.author.id}"
        if key not in self.xp_data:
            self.xp_data[key] = {"xp": 0, "level": 1}

        # Add random XP (prevents exact-timing spam)
        self.xp_data[key]["xp"] += random.randint(5, 15)
        
        xp = self.xp_data[key]["xp"]
        new_level = int(xp ** 0.5) // 10 + 1  # Better scaling formula
        
        if new_level > self.xp_data[key]["level"]:
            self.xp_data[key]["level"] = new_level
            await message.channel.send(f"🎉 {message.author.mention} reached Level {new_level}!")

    @commands.command()
    async def rank(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        key = f"{ctx.guild.id}_{target.id}"
        
        if key not in self.xp_data:
            await ctx.send(f"{target.name} has no rank yet. Start chatting!")
            return

        data = self.xp_data[key]
        embed = discord.Embed(title=f"📊 {target.name}'s Rank", color=0x2ecc71)
        embed.add_field(name="Level", value=data["level"], inline=True)
        embed.add_field(name="Total XP", value=data["xp"], inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def leaderboard(self, ctx):
        # Filter XP data for current guild ONLY
        guild_prefix = f"{ctx.guild.id}_"
        guild_xp = {
            user_id.replace(guild_prefix, ""): data 
            for user_id, data in self.xp_data.items() 
            if user_id.startswith(guild_prefix)
        }
        
        sorted_xp = sorted(guild_xp.items(), key=lambda x: x[1]["xp"], reverse=True)[:5]
        
        if not sorted_xp:
            await ctx.send("No XP data available for this server yet.")
            return

        embed = discord.Embed(title="🏆 Server Leaderboard", color=0xf1c40f)
        for i, (user_id, data) in enumerate(sorted_xp, start=1):
            # Uses cache instead of slow API fetch
            member = ctx.guild.get_member(int(user_id))
            name = member.display_name if member else f"Unknown User ({user_id})"
            embed.add_field(
                name=f"#{i} {name}", 
                value=f"Level {data['level']} | {data['xp']} XP", 
                inline=False
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leveling(bot))
