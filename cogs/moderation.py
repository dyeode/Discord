import asyncio
from datetime import datetime
import discord
from discord.ext import commands
from utils.data import load_data, save_data

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.muted_file = 'muted_members.json'
        self.data = load_data(self.muted_file)
        self.ban_data = load_data("ban_history.json", default={})
    
    def save_ban_data(self):
        save_data("ban_history.json", self.ban_data)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        try:
            await member.kick(reason=reason)
            await ctx.send(f"{member.mention} has been kicked. Reason: {reason if reason else 'No reason provided.'}")
        except Exception as e:
            await ctx.send(f"Failed to kick {member.mention}. Error: {e}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        try:
            await member.ban(reason=reason)
            await ctx.send(f"{member.mention} has been banned. Reason: {reason if reason else 'No reason provided.'}")
        except Exception as e:
            await ctx.send(f"Failed to ban {member.mention}. Error: {e}")
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        user_id = str(user.id)
        if user_id not in self.ban_data:
            self.ban_data[user_id] = []

        reason = "No reason provided"
        ban_entry = await guild.bans()
        for entry in ban_entry:
            if entry.user.id == user.id:
                reason = entry.reason or reason

        self.ban_data[user_id].append({
            "server_name": guild.name,
            "server_id": str(guild.id),
            "reason": reason,
            "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        })
        self.save_ban_data()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def check_ban(self, ctx, user: discord.User):
        user_id = str(user.id)
        if user_id in self.ban_data:
            ban_history = self.ban_data[user_id]
            embed = discord.Embed(
                title=f"Ban History for {user.name}",
                color=discord.Color.red()
            )
            for entry in ban_history:
                embed.add_field(
                    name=f"Server: {entry['server_name']} (ID: {entry['server_id']})",
                    value=f"**Reason:** {entry['reason']}\n**Date:** {entry['date']}",
                    inline=False
                )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"✅ {user.name} has no ban history logged.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clear_ban(self, ctx, user: discord.User):
        user_id = str(user.id)
        if user_id in self.ban_data:
            del self.ban_data[user_id]
            self.save_ban_data()
            await ctx.send(f"✅ Ban history for {user.name} has been cleared.")
        else:
            await ctx.send(f"⚠️ No ban history found for {user.name}.")
    
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def massban(self, ctx, *member_ids: int):
        failed = []
        for member_id in member_ids:
            member = ctx.guild.get_member(member_id)
            if member:
                try:
                    await member.ban(reason="Mass ban by moderation command.")
                except Exception:
                    failed.append(member_id)
            else:
                failed.append(member_id)

        if failed:
            await ctx.send(f"Could not ban the following IDs: {', '.join(map(str, failed))}")
        else:
            await ctx.send("All specified members have been banned.")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member_name):
        banned_users = await ctx.guild.bans()
        for ban_entry in banned_users:
            user = ban_entry.user
            if user.name == member_name:
                await ctx.guild.unban(user)
                await ctx.send(f"{user.name} has been unbanned.")
                return
        await ctx.send(f"User {member_name} not found in the ban list.")

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
        save_data(self.muted_file, self.data)
        await ctx.send(f"{member.mention} has been muted. Reason: {reason if reason else 'No reason provided.'}")
    
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def tempmute(self, ctx, member: discord.Member, duration: int, *, reason=None):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, speak=False, send_messages=False)
        
        await member.add_roles(muted_role, reason=reason)
        await ctx.send(f"{member.mention} has been muted for {duration} seconds. Reason: {reason if reason else 'No reason provided.'}")
        
        await asyncio.sleep(duration)
        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            await ctx.send(f"{member.mention} has been unmuted.")


    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            self.data.pop(str(member.id), None)
            save_data(self.muted_file, self.data)
            await ctx.send(f"{member.mention} has been unmuted.")
        else:
            await ctx.send(f"{member.mention} is not muted.")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def muted(self, ctx):
        if not self.data:
            await ctx.send("No members are currently muted.")
            return

        muted_list = "\n".join([f"<@{member_id}>: {reason}" for member_id, reason in self.data.items()])
        await ctx.send(f"Currently muted members:\n{muted_list}")
    
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason=None):
        warnings_file = "warnings.json"
        warnings = load_data(warnings_file)

        if str(member.id) not in warnings:
            warnings[str(member.id)] = []

        warnings[str(member.id)].append(reason or "No reason provided.")
        save_data(warnings_file, warnings)

        await ctx.send(f"{member.mention} has been warned. Reason: {reason if reason else 'No reason provided.'}")
    
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warnings(self, ctx, member: discord.Member):
        warnings_file = "warnings.json"
        warnings = load_data(warnings_file)

        if str(member.id) in warnings and warnings[str(member.id)]:
            warnings_list = "\n".join([f"{idx + 1}. {reason}" for idx, reason in enumerate(warnings[str(member.id)])])
            await ctx.send(f"Warnings for {member.mention}:\n{warnings_list}")
        else:
            await ctx.send(f"{member.mention} has no warnings.")
    
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear_warnings(self, ctx, member: discord.Member):
        warnings_file = "warnings.json"
        warnings = load_data(warnings_file)

        if str(member.id) in warnings:
            warnings.pop(str(member.id))
            save_data(warnings_file, warnings)
            await ctx.send(f"Cleared all warnings for {member.mention}.")
        else:
            await ctx.send(f"{member.mention} has no warnings to clear.")
    
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int):
        try:
            await ctx.channel.edit(slowmode_delay=seconds)
            await ctx.send(f"Slowmode has been set to {seconds} seconds.")
        except Exception as e:
            await ctx.send(f"Failed to set slowmode. Error: {e}")
    
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        try:
            deleted = await ctx.channel.purge(limit=amount)
            await ctx.send(f"Deleted {len(deleted)} messages.", delete_after=5)
        except Exception as e:
            await ctx.send(f"Failed to purge messages. Error: {e}")
    
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        try:
            overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
            overwrite.send_messages = False
            await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            await ctx.send("This channel has been locked.")
        except Exception as e:
            await ctx.send(f"Failed to lock the channel. Error: {e}")
    
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        try:
            overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
            overwrite.send_messages = True
            await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            await ctx.send("This channel has been unlocked.")
        except Exception as e:
            await ctx.send(f"Failed to unlock the channel. Error: {e}")
    
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, member: discord.Member, *, role_name):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            await member.add_roles(role)
            await ctx.send(f"{role.name} has been added to {member.mention}.")
        else:
            await ctx.send(f"Role '{role_name}' not found.")
    
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx, member: discord.Member, *, role_name):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role and role in member.roles:
            await member.remove_roles(role)
            await ctx.send(f"{role.name} has been removed from {member.mention}.")
        else:
            await ctx.send(f"{member.mention} does not have the role '{role_name}' or it doesn't exist.")
    
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def cleanchannel(self, ctx):
        try:
            new_channel = await ctx.channel.clone()
            await ctx.channel.delete()
            await ctx.send(f"Channel {new_channel.mention} has been cleaned.")
        except Exception as e:
            await ctx.send(f"Failed to clean the channel. Error: {e}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def add_blacklist(self, ctx, *, word: str):
        blacklist_file = "blacklist.json"
        blacklist = load_data(blacklist_file)
        
        if word.lower() in blacklist:
            await ctx.send(f"'{word}' is already in the blacklist.")
            return
        
        blacklist.append(word.lower())
        save_data(blacklist_file, blacklist)
        await ctx.send(f"'{word}' has been added to the blacklist.")
    
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def remove_blacklist(self, ctx, *, word: str):
        blacklist_file = "blacklist.json"
        blacklist = load_data(blacklist_file)
        
        if word.lower() not in blacklist:
            await ctx.send(f"'{word}' is not in the blacklist.")
            return
        
        blacklist.remove(word.lower())
        save_data(blacklist_file, blacklist)
        await ctx.send(f"'{word}' has been removed from the blacklist.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def view_blacklist(self, ctx):
        blacklist_file = "blacklist.json"
        blacklist = load_data(blacklist_file)
        
        if not blacklist:
            await ctx.send("The blacklist is currently empty.")
        else:
            await ctx.send(f"Blacklisted words:\n{', '.join(blacklist)}")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            blacklist_file = "blacklist.json"
            blacklist = load_data(blacklist_file)
            
            if any(word in message.content.lower() for word in blacklist):
                await message.delete()
                await message.channel.send(f"{message.author.mention}, your message contained a blacklisted word and was removed.", delete_after=5)

async def setup(bot):
    await bot.add_cog(Moderation(bot))