import discord
from discord.ext import commands
import os

class Loader(commands.Cog):
    def __init__(self, bot: commands.Bot, cogs_dir: str = "cogs"):
        self.bot = bot
        self.cogs_dir = cogs_dir

    @commands.command(name="load", hidden=True)
    @commands.is_owner()
    async def load_cog(self, ctx, cog: str):
        """Load a specific cog."""
        try:
            await self.bot.load_extension(f"{self.cogs_dir}.{cog}")
            await ctx.send(f"✅ Successfully loaded the cog: `{cog}`.")
        except commands.ExtensionAlreadyLoaded:
            await ctx.send(f"⚠️ The cog `{cog}` is already loaded.")
        except commands.ExtensionNotFound:
            await ctx.send(f"⚠️ The cog `{cog}` was not found.")
        except Exception as e:
            await ctx.send(f"⚠️ Failed to load the cog `{cog}`. Error: {e}")

    @commands.command(name="unload", hidden=True)
    @commands.is_owner()
    async def unload_cog(self, ctx, cog: str):
        """Unload a specific cog."""
        try:
            await self.bot.unload_extension(f"{self.cogs_dir}.{cog}")
            await ctx.send(f"✅ Successfully unloaded the cog: `{cog}`.")
        except commands.ExtensionNotLoaded:
            await ctx.send(f"⚠️ The cog `{cog}` is not loaded.")
        except Exception as e:
            await ctx.send(f"⚠️ Failed to unload the cog `{cog}`. Error: {e}")

    @commands.command(name="reload", hidden=True)
    @commands.is_owner()
    async def reload_cog(self, ctx, cog: str):
        """Reload a specific cog."""
        try:
            await self.bot.unload_extension(f"{self.cogs_dir}.{cog}")
            await self.bot.load_extension(f"{self.cogs_dir}.{cog}")
            await ctx.send(f"🔄 Successfully reloaded the cog: `{cog}`.")
        except commands.ExtensionNotFound:
            await ctx.send(f"⚠️ The cog `{cog}` was not found.")
        except Exception as e:
            await ctx.send(f"⚠️ Failed to reload the cog `{cog}`. Error: {e}")

    async def reset_and_load_all_cogs(self):
        """Unload all cogs and load them again to reset the state."""
        # Unload all currently loaded extensions
        for ext in list(self.bot.extensions.keys()):
            try:
                await self.bot.unload_extension(ext)
                print(f"🔄 Unloaded `{ext}`.")
            except Exception as e:
                print(f"⚠️ Failed to unload `{ext}`. Error: {e}")

        # Load all cogs from the cogs directory
        for filename in os.listdir(self.cogs_dir):
            if filename.endswith(".py") and filename != "loader.py":
                cog_name = filename[:-3]  # Strip `.py` extension
                try:
                    await self.bot.load_extension(f"{self.cogs_dir}.{cog_name}")
                    print(f"✅ Successfully loaded `{cog_name}`.")
                except Exception as e:
                    print(f"⚠️ Failed to load `{cog_name}`. Error: {e}")

async def setup(bot: commands.Bot):
    """Set up the loader cog and reset/load all cogs."""
    loader = Loader(bot)
    await loader.reset_and_load_all_cogs()
    await bot.add_cog(loader)
