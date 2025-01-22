import discord
import json
from discord.ext import commands
from datetime import datetime

class Backup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def backup(self, ctx):
        guild = ctx.guild
        backup_data = {
            "server_name": guild.name,
            "server_id": guild.id,
            "roles": [
                {"name": role.name, "permissions": role.permissions.value, "color": str(role.color)}
                for role in guild.roles if not role.is_default()
            ],
            "channels": [
                {"name": channel.name, "id": channel.id, "type": str(channel.type)}
                for channel in guild.channels
            ],
            "members": [
                {"name": member.name, "id": member.id, "roles": [role.name for role in member.roles if not role.is_default()]}
                for member in guild.members
            ],
        }

        filename = f"backup_{guild.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(backup_data, f, indent=4)
        
        await ctx.send(f"✅ Backup completed. Saved as `{filename}`.")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def load_backup(self, ctx, filename: str):
        try:
            with open(filename, "r") as f:
                backup_data = json.load(f)
            
            embed = discord.Embed(
                title="Backup Details",
                description=f"Backup for server: {backup_data['server_name']}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Roles Count", value=len(backup_data["roles"]), inline=True)
            embed.add_field(name="Channels Count", value=len(backup_data["channels"]), inline=True)
            embed.add_field(name="Members Count", value=len(backup_data["members"]), inline=True)
            await ctx.send(embed=embed)
        except FileNotFoundError:
            await ctx.send(f"⚠️ File `{filename}` not found.")
        except Exception as e:
            await ctx.send(f"⚠️ Failed to load backup: {e}")

async def setup(bot):
    await bot.add_cog(Backup(bot))