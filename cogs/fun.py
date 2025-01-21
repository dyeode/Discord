import discord
import random
import asyncio
from discord.ext import commands
from utils.data import load_fun_data

class FunCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = load_fun_data()

    @commands.command()
    async def dadjoke(self, ctx):
        jokes = self.data.get("dadjokes", [])
        if jokes:
            await ctx.send(f"😂 {random.choice(jokes)}")
        else:
            await ctx.send("No dad jokes available right now.")

    @commands.command()
    async def compliment(self, ctx, member: discord.Member):
        compliments = self.data.get("compliments", [])
        if compliments:
            await ctx.send(f"{member.mention}, {random.choice(compliments)} 😊")
        else:
            await ctx.send("No compliments available right now.")

    @commands.command()
    async def trivia(self, ctx):
        trivia_data = self.data.get("trivia", {})
        if trivia_data:
            question, answer = random.choice(list(trivia_data.items()))
            await ctx.send(f"🧠 Trivia Time! {question}")

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel

            try:
                response = await self.bot.wait_for("message", timeout=15.0, check=check)
                if response.content.lower() == answer.lower():
                    await ctx.send("🎉 Correct!")
                else:
                    await ctx.send(f"❌ Wrong! The correct answer was {answer}.")
            except asyncio.TimeoutError:
                await ctx.send(f"⏰ Time's up! The correct answer was {answer}.")
        else:
            await ctx.send("No trivia questions available right now.")

    @commands.command()
    async def wouldyourather(self, ctx):
        questions = self.data.get("wouldyourather", [])
        if questions:
            await ctx.send(f"🤔 {random.choice(questions)}")
        else:
            await ctx.send("No 'Would You Rather' questions available right now.")

    @commands.command()
    async def fact(self, ctx):
        facts = self.data.get("facts", [])
        if facts:
            await ctx.send(f"🌟 Fun Fact: {random.choice(facts)}")
        else:
            await ctx.send("No fun facts available right now.")

async def setup(bot):
    await bot.add_cog(FunCommands(bot))