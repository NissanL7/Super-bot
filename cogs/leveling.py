import discord
from discord.ext import commands
import sqlite3
import random

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_file = "bot_data.db"
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database and create tables if they don't exist."""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS xp (
                    guild_id INTEGER,
                    user_id INTEGER,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    PRIMARY KEY (guild_id, user_id)
                )
            """)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        # Small chance to ignore messages to prevent spam farming
        if random.randint(1, 5) != 1:
            return

        guild_id = message.guild.id
        user_id = message.author.id

        try:
            with sqlite3.connect(self.db_file) as conn:
                # Upsert: Insert or update XP
                conn.execute("""
                    INSERT INTO xp (guild_id, user_id, xp, level)
                    VALUES (?, ?, 10, 1)
                    ON CONFLICT(guild_id, user_id) 
                    DO UPDATE SET xp = xp + 10
                """, (guild_id, user_id))
                
                # Fetch new XP and calculate level
                cursor = conn.execute("SELECT xp, level FROM xp WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
                row = cursor.fetchone()
              if row:
                    new_xp, old_level = row
                    new_level = int(new_xp ** 0.5) // 10 + 1
                    
                    # Update level if it increased
                    if new_level > old_level:
                        conn.execute("UPDATE xp SET level = ? WHERE guild_id = ? AND user_id = ?", (new_level, guild_id, user_id))
                        await message.channel.send(f"🎉 {message.author.mention} reached Level {new_level}!")
        except Exception as e:
            print(f"Database error: {e}")

    @commands.command()
    async def rank(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        guild_id = ctx.guild.id
        user_id = target.id

        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.execute(
                "SELECT level, xp FROM xp WHERE guild_id = ? AND user_id = ?", 
                (guild_id, user_id)
            )
            result = cursor.fetchone()

        if not result:
            await ctx.send(f"{target.name} has no rank yet. Start chatting!")
            return

        level, xp = result
        embed = discord.Embed(title=f"📊 {target.name}'s Rank", color=0x2ecc71)
        embed.add_field(name="Level", value=level, inline=True)
        embed.add_field(name="Total XP", value=xp, inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def leaderboard(self, ctx):
        guild_id = ctx.guild.id
        
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.execute(
                "SELECT user_id, xp, level FROM xp WHERE guild_id = ? ORDER BY xp DESC LIMIT 5", 
                (guild_id,)
            )
            top_users = cursor.fetchall()

        if not top_users:
            await ctx.send("No XP data available for this server yet.")
            return

        embed = discord.Embed(title="🏆 Server Leaderboard", color=0xf1c40f)
        for i, (user_id, xp, level) in enumerate(top_users, start=1):
            member = ctx.guild.get_member(int(user_id))
            name = member.display_name if member else f"Unknown User ({user_id})"
            embed.add_field(name=f"#{i} {name}", value=f"Level {level} | {xp} XP", inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leveling(bot))
    @commands.command()
    async def rank(self, ctx, member: discord.Member = None):
        # PREVENTS CRASHES IN DMs
        if not ctx.guild:
            return await ctx.send("⚠️ You can only use this command inside a server!")
            
        target = member or ctx.author
        guild_id = ctx.guild.id
        user_id = target.id

        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.execute(
                "SELECT level, xp FROM xp WHERE guild_id = ? AND user_id = ?", 
                (guild_id, user_id)
            )
            result = cursor.fetchone()

        if not result:
            await ctx.send(f"{target.name} has no rank yet. Start chatting!")
            return

        level, xp = result
        embed = discord.Embed(title=f"📊 {target.name}'s Rank", color=0x2ecc71)
        embed.add_field(name="Level", value=level, inline=True)
        embed.add_field(name="Total XP", value=xp, inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def leaderboard(self, ctx):
        # PREVENTS CRASHES IN DMs
        if not ctx.guild:
            return await ctx.send("⚠️ You can only use this command inside a server!")
            
        guild_id = ctx.guild.id
        
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.execute(
                "SELECT user_id, xp, level FROM xp WHERE guild_id = ? ORDER BY xp DESC LIMIT 5", 
                (guild_id,)
            )
            top_users = cursor.fetchall()

        if not top_users:
            await ctx.send("No XP data available for this server yet.")
            return

        embed = discord.Embed(title="🏆 Server Leaderboard", color=0xf1c40f)
        for i, (user_id, xp, level) in enumerate(top_users, start=1):
            member = ctx.guild.get_member(int(user_id))
            name = member.display_name if member else f"Unknown User ({user_id})"
            embed.add_field(name=f"#{i} {name}", value=f"Level {level} | {xp} XP", inline=False)
        
        await ctx.send(embed=embed)
