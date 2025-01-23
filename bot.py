import discord
from discord.ext import commands
import asyncio
import os
from utils import load_config

config = load_config()

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix=config.get("prefix", "!"),
    intents=intents,
    description="A moderation and server management bot."
)

@bot.event
async def on_ready(): # When the bot is ready to be used (logged in)
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")
    print("Bot is ready and listening for commands!")

@bot.event
async def on_command_error(ctx, error): # When a command has an error or is not found (command not found)
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("⚠️ You don't have the necessary permissions to execute this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Please provide all required arguments for this command.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❓ Command not found. Use `!help` to see available commands.")
    else:
        await ctx.send("⚠️ An unexpected error occurred. Please contact the admin.")
        print(f"Unexpected error: {error}")

async def load_all_cogs(): # Load all cogs in the cogs directory when the bot starts up (loads all commands)
    cogs_dir = "./cogs"
    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py"):
            cog_name = filename[:-3]
            if f"cogs.{cog_name}" in bot.extensions:
                print(f"⚠️ Cog `{cog_name}` is already loaded. Skipping.")
                continue
            try:
                await bot.load_extension(f"cogs.{cog_name}")
                print(f"✅ Loaded cog: {cog_name}")
            except commands.errors.CommandRegistrationError as e:
                print(f"⚠️ Failed to load cog `{cog_name}`: Duplicate command name.")
            except Exception as e:
                print(f"⚠️ Failed to load cog `{cog_name}`: {e}")

async def main(): # Main function to start the bot and load all cogs (commands)
    print("Starting bot...")
    await load_all_cogs()
    token = config.get("token")
    if not token:
        print("⚠️ Token is missing in the configuration.")
        return
    await bot.start(token)

if __name__ == "__main__": # Run the main function if the script is executed directly (not imported)
    asyncio.run(main())