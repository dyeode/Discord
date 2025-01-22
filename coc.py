import discord
from discord.ext import commands
import requests
import json

class ClashOfClans(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_base_url = "https://api.clashofclans.com/v1"
        self.api_token = self.load_api_token()

    def load_api_token(self):
        """Load the API token from config.json."""
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                token = config.get("coc_api_token")
                if not token:
                    raise ValueError("⚠️ coc_api_token is missing in config.json.")
                return token
        except FileNotFoundError:
            raise Exception("⚠️ config.json not found. Please create it and add your API token.")
        except Exception as e:
            raise Exception(f"⚠️ Failed to load API token. Error: {e}")

    def make_request(self, endpoint):
        """Make a GET request to the Clash of Clans API."""
        url = f"{self.api_base_url}{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_token}"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise Exception("⚠️ Resource not found.")
        else:
            raise Exception(f"⚠️ API request failed: {response.status_code} - {response.text}")

    @commands.command()
    async def clan(self, ctx, clan_tag: str):
        """Fetch and display information about a clan."""
        try:
            clan_tag = clan_tag.strip("#").upper()
            data = self.make_request(f"/clans/%23{clan_tag}")

            embed = discord.Embed(
                title=f"Clan Info: {data['name']}",
                description=f"Tag: #{data['tag']}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Level", value=data["clanLevel"], inline=True)
            embed.add_field(name="Members", value=data["members"], inline=True)
            embed.add_field(name="Type", value=data["type"].capitalize(), inline=True)
            embed.add_field(name="Description", value=data.get("description", "No description"), inline=False)
            embed.add_field(name="War Wins", value=data.get("warWins", "Unknown"), inline=True)
            embed.add_field(name="War League", value=data.get("warLeague", {}).get("name", "Unranked"), inline=True)
            embed.set_thumbnail(url=data["badgeUrls"]["large"])
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"⚠️ Could not fetch clan info. Error: {e}")

    @commands.command()
    async def player(self, ctx, player_tag: str):
        """Fetch and display information about a player."""
        try:
            player_tag = player_tag.strip("#").upper()
            data = self.make_request(f"/players/%23{player_tag}")

            embed = discord.Embed(
                title=f"Player Info: {data['name']}",
                description=f"Tag: {data['tag']}",
                color=discord.Color.green()
            )
            embed.add_field(name="Town Hall Level", value=data["townHallLevel"], inline=True)
            embed.add_field(name="Exp Level", value=data["expLevel"], inline=True)
            embed.add_field(name="Trophies", value=data["trophies"], inline=True)
            embed.add_field(name="Best Trophies", value=data["bestTrophies"], inline=True)
            embed.add_field(name="Clan", value=data.get("clan", {}).get("name", "No clan"), inline=False)
            embed.add_field(name="Role", value=data.get("role", "No role").capitalize(), inline=True)
            embed.add_field(name="Donations", value=data.get("donations", 0), inline=True)
            embed.set_thumbnail(url=data.get("league", {}).get("iconUrls", {}).get("large", ""))
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"⚠️ Could not fetch player info. Error: {e}")

    @commands.command()
    async def warlog(self, ctx, clan_tag: str):
        """Fetch and display the war log of a clan."""
        try:
            clan_tag = clan_tag.strip("#").upper()
            data = self.make_request(f"/clans/%23{clan_tag}/warlog")

            if not data["items"]:
                await ctx.send("⚠️ This clan has no war log available.")
                return

            embed = discord.Embed(
                title=f"War Log for Clan #{clan_tag}",
                color=discord.Color.purple()
            )
            for war in data["items"][:5]:  # Show the last 5 wars
                result = war.get("result", "Unknown").capitalize()
                opponent = war["opponent"]["name"]
                stars = war["clan"]["stars"]
                embed.add_field(
                    name=f"Against {opponent}",
                    value=f"Result: {result}\nStars: {stars}",
                    inline=False
                )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"⚠️ Could not fetch war log. Error: {e}")

# Add the setup function
async def setup(bot):
    await bot.add_cog(ClashOfClans(bot))