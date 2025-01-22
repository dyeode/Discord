import asyncio
from datetime import datetime
import discord
from discord.ext import commands
from utils import (
    load_ban_data, save_ban_data, 
    load_muted_data, save_muted_data, 
    load_blacklist, save_blacklist
)

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.data = load_muted_data()
        self.ban_data = load_ban_data()

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        try:
            await member.ban(reason=reason)
            await ctx.send(f"{member.mention} has been banned. Reason: {reason or 'No reason provided.'}")
            self.ban_data.setdefault(str(member.id), []).append({
                "server_name": ctx.guild.name,
                "server_id": str(ctx.guild.id),
                "reason": reason or "No reason provided.",
                "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            })
            save_ban_data(self.ban_data)
        except Exception as e:
            await ctx.send(f"Failed to ban {member.mention}. Error: {e}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, reason=None):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, speak=False, send_messages=False)

        await member.add_roles(muted_role, reason=reason)
        self.data[str(member.id)] = reason or "No reason provided."
        save_muted_data(self.data)
        await ctx.send(f"{member.mention} has been muted. Reason: {reason or 'No reason provided.'}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            self.data.pop(str(member.id), None)
            save_muted_data(self.data)
            await ctx.send(f"{member.mention} has been unmuted.")
        else:
            await ctx.send(f"{member.mention} is not muted.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        blacklist = load_blacklist()
        if any(word in message.content.lower() for word in blacklist):
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, your message contained a blacklisted word and was removed.",
                delete_after=5
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))