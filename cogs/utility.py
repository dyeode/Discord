import asyncio
import discord
from discord.ext import commands
from datetime import datetime
from utils import load_data, save_data

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")
        self.help_data = load_data("help_data.json", default={})

    @commands.command()
    async def help(self, ctx, command_name: str = None):
        if not command_name:
            command_list = "\n".join(f"`{cmd}`: {info['description']}" for cmd, info in self.help_data.items())
            embed = discord.Embed(
                title="Help - List of Commands",
                description=f"Use `!help <command>` to get details about a specific command.\n\n{command_list}",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
        else:
            command_info = self.help_data.get(command_name.lower())
            if not command_info:
                await ctx.send(f"⚠️ Command `{command_name}` not found.")
                return

            embed = discord.Embed(
                title=f"Help - {command_name}",
                color=discord.Color.green()
            )
            embed.add_field(name="Description", value=command_info["description"], inline=False)
            embed.add_field(name="Usage", value=f"`{command_info['usage']}`", inline=False)
            embed.add_field(name="Example", value=f"`{command_info['example']}`", inline=False)
            await ctx.send(embed=embed)
    
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
    async def poll(self, ctx, *, args: str):
        try:
            if '"' in args:
                heading, question = args.split('"', 2)[1], args.split('"', 2)[2].strip()
            else:
                raise ValueError("Heading must be enclosed in quotes.")
            
            embed = discord.Embed(
                title=heading,
                description=question,
                color=discord.Color.gold()
            )
            message = await ctx.send(embed=embed)

            await message.add_reaction("👍")
            await message.add_reaction("👎")
        except ValueError:
            await ctx.send("⚠️ Usage: !poll \"Poll Heading\" Your poll question here.")
        except Exception as e:
            await ctx.send(f"⚠️ An error occurred: {e}")
    
    @commands.command()
    async def remind(self, ctx, time: int, *, message: str):
        await ctx.send(f"⏰ Reminder set for {time} seconds.")
        await asyncio.sleep(time)
        await ctx.send(f"⏰ Reminder: {message}")

async def setup(bot):
    await bot.add_cog(Utility(bot))