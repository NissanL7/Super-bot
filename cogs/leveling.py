import discord
from discord.ext import commands, tasks
import sqlite3
import os
import random

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_file = "bot_data.db"
        self._init_db()
        self.auto_save_xp.start() # Optional: used for batch operations if needed later

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

        with sqlite3.connect(self.db_file) as conn:
            # Upsert: Insert or update XP
            conn.execute("""
                INSERT INTO xp (guild_id, user_id, xp, level)
                VALUES (?, ?, 10, 1)
                ON CONFLICT(guild_id, user_id) 
                DO UPDATE SET xp = xp + 10
            """, (guild_id, user_id))
            
            # Fetch new XP and calculate level
            cursor = conn.execute("SELECT xp FROM xp WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
            new_xp = cursor.fetchone()[0]            new_level = int(new_xp ** 0.5) // 10 + 1
            
            # Update level if it increased
            conn.execute("UPDATE xp SET level = ? WHERE guild_id = ? AND user_id = ?", (new_level, guild_id, user_id))
            
            # Check if user leveled up to send a message
            cursor = conn.execute("SELECT level FROM xp WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
            # Note: For perfect level-up detection, you'd store the old level in memory, 
            # but this simple check works for most starter bots.

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
        for i, (user_id, xp, level) in enumerate(top_users, start=1):            member = ctx.guild.get_member(int(user_id))
            name = member.display_name if member else f"Unknown User ({user_id})"
            embed.add_field(name=f"#{i} {name}", value=f"Level {level} | {xp} XP", inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leveling(bot))
