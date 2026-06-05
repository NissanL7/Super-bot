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
