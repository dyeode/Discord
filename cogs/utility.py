import asyncio
import discord
from discord.ext import commands
from datetime import datetime

def command_error_handler(func):
    async def wrapper(self, ctx, *args, **kwargs):
        try:
            await func(self, ctx, *args, **kwargs)
        except Exception as e:
            await ctx.send(f"⚠️ An error occurred: {e}")
    return wrapper

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")

    @commands.command()
    async def help(self, ctx, command_name: str = None):
        if not command_name:
            embed = discord.Embed(
                title="Help - List of Commands",
                description="Use `?help <command>` to get details about a specific command.",
                color=discord.Color.blue()
            )
            for command in self.bot.commands:
                if not command.hidden:
                    embed.add_field(name=command.name, value=command.help or "No description provided.", inline=False)
            await ctx.send(embed=embed)
        else:
            command = self.bot.get_command(command_name)
            if command:
                embed = discord.Embed(
                    title=f"Help - {command.name}",
                    color=discord.Color.green()
                )
                embed.add_field(name="Description", value=command.help or "No description provided.", inline=False)
                embed.add_field(name="Usage", value=f"`{command.usage or 'Not specified'}`", inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"⚠️ Command `{command_name}` not found.")

    @commands.command()
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! Latency is `{latency}ms`.")

    @commands.command()
    async def serverinfo(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(
            title=f"Server Info - {guild.name}",
            description="Here are the details of this server.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Server ID", value=guild.id, inline=False)
        embed.add_field(name="Owner", value=guild.owner, inline=False)
        embed.add_field(name="Created At", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.add_field(name="Members", value=guild.member_count, inline=False)
        embed.set_thumbnail(url=guild.icon.url if guild.icon else discord.Embed.Empty)
        await ctx.send(embed=embed)

    @commands.command()
    async def avatar(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(
            title=f"{member}'s Avatar",
            color=discord.Color.green()
        )
        embed.set_image(url=member.avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def roleinfo(self, ctx, *, role: discord.Role):
        embed = discord.Embed(
            title=f"Role Info - {role.name}",
            color=role.color
        )
        embed.add_field(name="Role ID", value=role.id, inline=False)
        embed.add_field(name="Created At", value=role.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.add_field(name="Members", value=len(role.members), inline=False)
        embed.add_field(name="Permissions", value=', '.join(perm[0] for perm in role.permissions if perm[1]), inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def poll(self, ctx, heading: str, *, question: str):
        embed = discord.Embed(
            title=heading,
            description=question,
            color=discord.Color.gold()
        )
        message = await ctx.send(embed=embed)
        await message.add_reaction("👍")
        await message.add_reaction("👎")

    @commands.command()
    async def remind(self, ctx, time: int, *, message: str):
        await ctx.send(f"⏰ Reminder set for {time} seconds.")
        await asyncio.sleep(time)
        await ctx.send(f"⏰ Reminder: {message}")

    @commands.command()
    async def uptime(self, ctx):
        now = datetime.utcnow()
        uptime = now - self.bot.launch_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        await ctx.send(f"⏱️ Bot uptime: {hours}h {minutes}m {seconds}s.")

async def setup(bot):
    bot.launch_time = datetime.utcnow()
    await bot.add_cog(Utility(bot))