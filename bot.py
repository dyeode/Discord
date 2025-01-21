import discord
from discord.ext import commands
import asyncio
import json

from utils import load_config
config = load_config()

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=config["prefix"], intents=intents, description="A moderation and server management bot.")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")
    print("Bot is ready!")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have the necessary permissions to execute this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide all required arguments for this command.")
    else:
        await ctx.send(f"An error occurred: {error}")

async def main():
    await bot.load_extension("cogs.loader")
    await bot.start(config["token"])

asyncio.run(main())