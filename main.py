import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from aiohttp import web

# ============ ASYNC KEEP-ALIVE (for Render) ============
async def keep_alive():
    """Simple async web server for Render keep-alive"""
    app = web.Application()
    
    async def hello(request):
        return web.Response(text="🤖 Super Bot is running!")
    
    async def health(request):
        return web.json_response({"status": "ok"})
    
    app.router.add_get('/', hello)
    app.router.add_get('/health', health)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 8080)))
    await site.start()
    print(f"🌐 Keep-alive server running on port {os.getenv('PORT', 8080)}")
    return runner

# ============ DISCORD BOT SETUP ============
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print("❌ FATAL: DISCORD_TOKEN not found!")
    exit(1)

print(f"✅ Token found (length: {len(TOKEN)})")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ============ COG LOADER WITH DEBUG ============
async def load_cogs():
    cog_folder = "cogs"
    print(f"🔍 Looking for cogs in: {os.path.abspath(cog_folder)}")
    
    if not os.path.exists(cog_folder):
        print(f"❌ Folder '{cog_folder}' NOT FOUND!")
        return
    
    files = os.listdir(cog_folder)
    print(f"📁 Files in cogs/: {files}")
    
    for filename in files:
        if filename.endswith(".py") and not filename.startswith("__"):
            cog_name = filename[:-3]
            try:
                await bot.load_extension(f"{cog_folder}.{cog_name}")
                print(f"✅ Loaded cog: {cog_name}")
            except Exception as e:
                print(f"❌ Failed to load {cog_name}: {type(e).__name__}: {e}")

# ============ BOT EVENTS ============
@bot.event
async def on_ready():
    print(f"🟢 SUCCESS! {bot.user} is ONLINE and connected to Discord!")
    print(f"   → In {len(bot.guilds)} server(s)")
    print(f"   → Listening for commands...")

# ============ STARTUP ============
async def main():
    # Start keep-alive server first
    runner = await keep_alive()
    
    # Load cogs
    await load_cogs()
    
    # Connect to Discord
    print("🔑 Connecting to Discord...")
    async with bot:
        await bot.start(TOKEN)
    
    # Cleanup
    await runner.cleanup()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👋 Shutting down...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
