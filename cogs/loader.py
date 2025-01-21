import discord
from discord.ext import commands
import os

class Loader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="load", hidden=True)
    @commands.is_owner()
    async def load_cog(self, ctx, cog: str):
        try:
            await self.bot.load_extension(f"cogs.{cog}")
            await ctx.send(f"✅ Successfully loaded `{cog}`.")
        except Exception as e:
            await ctx.send(f"⚠️ Failed to load `{cog}`. Error: {e}")

    @commands.command(name="unload", hidden=True)
    @commands.is_owner()
    async def unload_cog(self, ctx, cog: str):
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            await ctx.send(f"✅ Successfully unloaded `{cog}`.")
        except Exception as e:
            await ctx.send(f"⚠️ Failed to unload `{cog}`. Error: {e}")

    @commands.command(name="reload", hidden=True)
    @commands.is_owner()
    async def reload_cog(self, ctx, cog: str):
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            await self.bot.load_extension(f"cogs.{cog}")
            await ctx.send(f"🔄 Successfully reloaded `{cog}`.")
        except Exception as e:
            await ctx.send(f"⚠️ Failed to reload `{cog}`. Error: {e}")

    async def load_all_cogs(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and filename != "loader.py":
                cog_name = filename[:-3]  # Remove `.py` extension
                try:
                    await self.bot.load_extension(f"cogs.{cog_name}")
                    print(f"✅ Loaded `{cog_name}`.")
                except Exception as e:
                    print(f"⚠️ Failed to load `{cog_name}`. Error: {e}")

async def setup(bot):
    loader = Loader(bot)
    await loader.load_all_cogs()  # Load all cogs on startup
    await bot.add_cog(loader)