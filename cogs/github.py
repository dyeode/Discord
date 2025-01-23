import discord
from discord.ext import commands
import requests
import json

class GitHub(commands.Cog):
    def __init__(self, bot): # Initialize the GitHub cog with the bot instance and set the base URL and token for GitHub API requests
        self.bot = bot
        self.base_url = "https://api.github.com" # Base URL for GitHub API requests (v3 version) (e.g., https://api.github.com)
        self.token = self.load_token()

    def load_token(self): # Load the GitHub API token from config.json file (create this file and add your token)
        try: # Try to load the GitHub token from the config.json file and return it.
            with open("config.json", "r") as f:
                config = json.load(f)
                token = config.get("github_token")
                if not token:
                    raise ValueError("⚠️ GitHub token is missing in config.json.")
                return token
        except FileNotFoundError:
            raise Exception("⚠️ config.json not found. Please create it and add your API token.")
        except Exception as e:
            raise Exception(f"⚠️ Failed to load GitHub token. Error: {e}")

    def make_request(self, endpoint, params=None):
        """
        Make a request to the GitHub API with the given endpoint and parameters (if any) and return the JSON response.
        """
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.token}",
        }
        response = requests.get(f"{self.base_url}{endpoint}", headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise Exception("⚠️ Resource not found.")
        else:
            raise Exception(f"⚠️ API request failed: {response.status_code} - {response.text}")

    @commands.command()
    async def repo(self, ctx, owner: str, repo: str): # Command to get information about a GitHub repository (e.g., ?repo discord discord-api-docs)
        try: # Try to fetch the repository information and send an embed with the details
            data = self.make_request(f"/repos/{owner}/{repo}")
            embed = discord.Embed(
                title=data["full_name"],
                description=data["description"] or "No description available.",
                color=discord.Color.blue(),
                url=data["html_url"]
            )
            embed.add_field(name="Stars", value=data["stargazers_count"], inline=True)
            embed.add_field(name="Forks", value=data["forks_count"], inline=True)
            embed.add_field(name="Open Issues", value=data["open_issues_count"], inline=True)
            embed.add_field(name="License", value=data["license"]["name"] if data["license"] else "None", inline=True)
            embed.set_thumbnail(url=data["owner"]["avatar_url"])
            await ctx.send(embed=embed)
        except Exception as e: # If an error occurs during the request, send an error message to the channel with details of the error (e.g., ?repo discord discord-api-docs)
            await ctx.send(f"⚠️ Could not fetch repository info. Error: {e}")

    @commands.command()
    async def user(self, ctx, username: str):
        try: # Try to fetch the user information and send an embed with the details (e.g., ?user discord)
            data = self.make_request(f"/users/{username}")
            embed = discord.Embed(
                title=data["login"],
                description=data["bio"] or "No bio available.",
                color=discord.Color.green(),
                url=data["html_url"]
            )
            embed.add_field(name="Public Repos", value=data["public_repos"], inline=True)
            embed.add_field(name="Followers", value=data["followers"], inline=True)
            embed.add_field(name="Following", value=data["following"], inline=True)
            embed.set_thumbnail(url=data["avatar_url"])
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"⚠️ Could not fetch user info. Error: {e}")

    @commands.command()
    async def search_repos(self, ctx, *, query: str): # Command to search GitHub repositories based on a query string (e.g., ?search_repos discord api)
        try: # Try to search repositories based on the query string and send an embed with the top results (e.g., ?search_repos discord api)
            data = self.make_request(f"/search/repositories", params={"q": query})
            embed = discord.Embed(
                title=f"Top Results for '{query}'",
                color=discord.Color.purple()
            )
            for item in data["items"][:5]: # Limit to top 5 results for brevity (e.g., ?search_repos discord api)
                embed.add_field(
                    name=item["full_name"],
                    value=f"[{item['html_url']}]({item['html_url']})\n⭐ {item['stargazers_count']} | 🍴 {item['forks_count']}",
                    inline=False
                )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"⚠️ Could not search repositories. Error: {e}")

async def setup(bot): # Setup function to add the cog to the bot (required by Discord.py) (e.g., bot.add_cog(GitHub(bot))) in bot.py file to load this cog (commands)
    await bot.add_cog(GitHub(bot))