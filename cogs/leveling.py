import discord
from discord.ext import commands
import json
import os
from datetime import datetime

class Leveling(commands.Cog):
    """XP and Leveling System"""
    
    def __init__(self, bot):
        self.bot = bot
        self.xp_file = "data/xp.json"
        self.cooldown_file = "data/cooldown.json"
        self.xp_data = {}
        self.cooldown_data = {}
        self.load_data()
    
    def load_data(self):
        """Load XP and cooldown data from files"""
        # Create data directory if not exists
        os.makedirs("data", exist_ok=True)
        
        # Load XP data
        if os.path.exists(self.xp_file):
            with open(self.xp_file, "r") as f:
                self.xp_data = json.load(f)
        else:
            self.xp_data = {}
        
        # Load cooldown data
        if os.path.exists(self.cooldown_file):
            with open(self.cooldown_file, "r") as f:
                self.cooldown_data = json.load(f)
        else:
            self.cooldown_data = {}
    
    def save_xp(self):
        """Save XP data to file"""
        with open(self.xp_file, "w") as f:
            json.dump(self.xp_data, f, indent=2)
    
    def save_cooldown(self):
        """Save cooldown data to file"""
        with open(self.cooldown_file, "w") as f:
            json.dump(self.cooldown_data, f, indent=2)
    
    def get_xp(self, user_id):
        """Get user's XP data"""
        if user_id not in self.xp_data:
            self.xp_data[user_id] = {"xp": 0, "level": 1}        return self.xp_data[user_id]
    
    def add_xp(self, user_id, amount):
        """Add XP to user and check for level up"""
        user_data = self.get_xp(user_id)
        user_data["xp"] += amount
        
        # Calculate new level
        old_level = user_data["level"]
        new_level = int(0.1 * (user_data["xp"]) ** 0.5) + 1
        
        if new_level > old_level:
            user_data["level"] = new_level
            self.save_xp()
            return True, old_level, new_level
        
        self.save_xp()
        return False, old_level, old_level
    
    def can_gain_xp(self, user_id):
        """Check if user can gain XP (cooldown system)"""
        current_time = datetime.now().timestamp()
        
        if user_id not in self.cooldown_data:
            self.cooldown_data[user_id] = 0
        
        last_xp_time = self.cooldown_data[user_id]
        cooldown = 60  # 60 seconds cooldown
        
        if current_time - last_xp_time >= cooldown:
            self.cooldown_data[user_id] = current_time
            self.save_cooldown()
            return True
        return False
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Award XP for messages"""
        if message.author.bot:
            return
        
        if not message.guild:
            return
        
        user_id = str(message.author.id)
        
        # Check cooldown
        if not self.can_gain_xp(user_id):
            return
                # Award XP (15-25 random)
        import random
        xp_amount = random.randint(15, 25)
        
        # Add XP and check for level up
        leveled_up, old_level, new_level = self.add_xp(user_id, xp_amount)
        
        if leveled_up:
            channel = message.channel
            embed = discord.Embed(
                title="🎉 LEVEL UP!",
                description=f"{message.author.mention} reached **Level {new_level}**!",
                color=discord.Color.gold()
            )
            embed.add_field(name="Previous Level", value=f"Level {old_level}", inline=True)
            embed.add_field(name="New Level", value=f"Level {new_level}", inline=True)
            embed.set_thumbnail(url=message.author.display_avatar.url)
            await channel.send(embed=embed)
    
    @commands.command()
    async def rank(self, ctx, member: discord.Member = None):
        """Show your or a member's rank"""
        if member is None:
            member = ctx.author
        
        user_id = str(member.id)
        user_data = self.get_xp(user_id)
        
        xp = user_data["xp"]
        level = user_data["level"]
        
        # Calculate XP needed for next level
        xp_needed = int(((level + 1 - 1) / 0.1) ** 2)
        xp_current = xp - int(((level - 1) / 0.1) ** 2) if level > 1 else xp
        
        # Create rank card
        embed = discord.Embed(
            title=f"📊 {member.display_name}'s Rank",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Level", value=f"**{level}**", inline=True)
        embed.add_field(name="Total XP", value=f"**{xp}**", inline=True)
        embed.add_field(name="Rank", value=f"#{self.get_user_rank(user_id)}", inline=True)
        embed.set_footer(text="Keep chatting to level up!")
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def leaderboard(self, ctx):        """Show top 10 users by XP"""
        if not self.xp_data:
            await ctx.send("No data yet. Start chatting to earn XP!")
            return
        
        # Sort by XP
        sorted_users = sorted(
            self.xp_data.items(),
            key=lambda x: x[1]["xp"],
            reverse=True
        )[:10]
        
        # Create leaderboard
        embed = discord.Embed(
            title="🏆 Server Leaderboard",
            description="Top 10 users by XP",
            color=discord.Color.gold()
        )
        
        for i, (user_id, data) in enumerate(sorted_users, 1):
            try:
                user = await self.bot.fetch_user(int(user_id))
                name = user.display_name
            except:
                name = f"User {user_id}"
            
            level = data["level"]
            xp = data["xp"]
            
            medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
            embed.add_field(
                name=f"{medal} {name}",
                value=f"Level {level} • {xp} XP",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def resetxp(self, ctx, member: discord.Member = None):
        """Reset XP (Admin only)"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need Administrator permission to use this command.")
            return
        
        if member is None:
            await ctx.send("❌ Please mention a user to reset.")
            return
        
        user_id = str(member.id)        if user_id in self.xp_data:
            del self.xp_data[user_id]
            self.save_xp()
            await ctx.send(f"✅ Reset XP for {member.mention}")
        else:
            await ctx.send(f"{member.mention} has no XP data.")
    
    def get_user_rank(self, user_id):
        """Get user's rank position"""
        if not self.xp_data:
            return 1
        
        user_xp = self.xp_data.get(user_id, {"xp": 0})["xp"]
        rank = 1
        
        for uid, data in self.xp_data.items():
            if data["xp"] > user_xp:
                rank += 1
        
        return rank

async def setup(bot):
    await bot.add_cog(Leveling(bot))
