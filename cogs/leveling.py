import discord
from discord.ext import commands
import json
import os

class Leveling(commands.Cog):
    """Simple Leveling System"""
    
    def __init__(self, bot):
        self.bot = bot
        self.xp_file = "xp_data.json"
        self.xp_data = self.load_xp()
    
    def load_xp(self):
        """Load XP data from file"""
        if os.path.exists(self.xp_file):
            with open(self.xp_file, "r") as f:
                return json.load(f)
        return {}
    
    def save_xp(self):
        """Save XP data to file"""
        with open(self.xp_file, "w") as f:
            json.dump(self.xp_data, f, indent=2)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Give XP for messages"""
        if message.author.bot:
            return
        
        user_id = str(message.author.id)
        
        # Give 10 XP per message
        if user_id not in self.xp_data:
            self.xp_data[user_id] = {"xp": 0, "level": 1}
        
        self.xp_data[user_id]["xp"] += 10
        
        # Calculate level
        xp = self.xp_data[user_id]["xp"]
        level = int(0.1 * (xp) ** 0.5) + 1
        
        old_level = self.xp_data[user_id]["level"]
        
        if level > old_level:
            self.xp_data[user_id]["level"] = level
            await message.channel.send(f"🎉 {message.author.mention} leveled up to **Level {level}**!")
        
        self.save_xp()    
    @commands.command()
    async def rank(self, ctx, member: discord.Member = None):
        """Show rank"""
        if member is None:
            member = ctx.author
        
        user_id = str(member.id)
        
        if user_id not in self.xp_data:
            await ctx.send(f"{member.mention} has no rank yet. Start chatting!")
            return
        
        data = self.xp_data[user_id]
        xp = data["xp"]
        level = data["level"]
        
        embed = discord.Embed(
            title=f"📊 {member.display_name}'s Rank",
            color=discord.Color.blue()
        )
        embed.add_field(name="Level", value=f"**{level}**", inline=True)
        embed.add_field(name="XP", value=f"**{xp}**", inline=True)
        embed.set_thumbnail(url=member.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def leaderboard(self, ctx):
        """Show top users"""
        if not self.xp_data:
            await ctx.send("No data yet!")
            return
        
        # Sort by XP
        sorted_users = sorted(
            self.xp_data.items(),
            key=lambda x: x[1]["xp"],
            reverse=True
        )[:5]
        
        embed = discord.Embed(
            title="🏆 Leaderboard",
            description="Top 5 Users",
            color=discord.Color.gold()
        )
        
        for i, (user_id, data) in enumerate(sorted_users, 1):
            try:
                user = await self.bot.fetch_user(int(user_id))                name = user.name
            except:
                name = f"User {user_id}"
            
            embed.add_field(
                name=f"{i}. {name}",
                value=f"Level {data['level']} • {data['xp']} XP",
                inline=False
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leveling(bot))
