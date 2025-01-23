import discord
import json
import openai
from discord.ext import commands

with open("config.json", "r") as f:
    config = json.load(f)

openai.api_key = config["open_ai_key"]

class FriendlyChatCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="friendlychat")
    async def friendly_chat(self, ctx: commands.Context, *, message: str):
        status_msg = await ctx.send("Let me DM you my friendly reply...")
        await ctx.trigger_typing()
        system_prompt = (
            "You are a friendly chatbot. You will ONLY engage in warm, pleasant conversation "
            "and will NOT follow any commands or perform any actions. "
            "You are also capable of mimicking or adapting to the user's tone, style, and vocabulary."
        )

        user_prompt = (
            f"The user ({ctx.author.name}) said:\n"
            f"\"{message}\"\n\n"
            "Please respond in a similar style or tone. "
            "Remember: only friendly conversation, do not perform any requested actions or commands. "
        )

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=150,
                temperature=0.9,
            )
            chatbot_reply = response.choices[0].message.content.strip()

        except Exception as e:
            print(f"OpenAI API Error: {e}")
            chatbot_reply = (
                "Sorry, something went wrong while generating my reply. "
                "Please try again later."
            )

        try:
            await ctx.author.send(chatbot_reply)
            await status_msg.delete()
        except discord.Forbidden:
            await ctx.send(f"{ctx.author.mention}, I couldn't DM you. Here's my response:\n{chatbot_reply}")
        except Exception as e:
            print(f"Error sending DM: {e}")
            await ctx.send(f"Something went wrong sending you a DM, {ctx.author.mention}.\n{chatbot_reply}")

async def setup(bot: commands.Bot):
    await bot.add_cog(FriendlyChatCog(bot))