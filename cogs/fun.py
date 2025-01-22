import io
import random
import discord
import asyncio
import requests
from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands
from utils import load_fun_data


def command_error_handler(func):
    async def _command_wrapper(self, ctx, *args, **kwargs):
        try:
            await func(self, ctx, *args, **kwargs)
        except Exception as e:
            await ctx.send(f"⚠️ An error occurred: {e}")
    return _command_wrapper


class FunCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = load_fun_data()

    def get_data(self, key):
        return self.data.get(key, [])

    @commands.command(name="dadjoke")
    @command_error_handler
    async def dadjoke(self, ctx):
        jokes = self.get_data("dadjokes")
        if jokes:
            await ctx.send(f"😂 {random.choice(jokes)}")
        else:
            await ctx.send("⚠️ No dad jokes available right now.")

    @commands.command(name="compliment")
    @command_error_handler
    async def compliment(self, ctx, member: discord.Member):
        compliments = self.get_data("compliments")
        if compliments:
            await ctx.send(f"{member.mention}, {random.choice(compliments)} 😊")
        else:
            await ctx.send("⚠️ No compliments available right now.")

    @commands.command(name="trivia")
    @command_error_handler
    async def trivia(self, ctx):
        trivia_data = self.get_data("trivia")
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
                    await ctx.send(f"❌ Wrong! The correct answer was: **{answer}**.")
            except asyncio.TimeoutError:
                await ctx.send(f"⏰ Time's up! The correct answer was: **{answer}**.")
        else:
            await ctx.send("⚠️ No trivia questions available right now.")

    @commands.command(name="wouldyourather")
    @command_error_handler
    async def wouldyourather(self, ctx):
        questions = self.get_data("wouldyourather")
        if questions:
            await ctx.send(f"🤔 {random.choice(questions)}")
        else:
            await ctx.send("⚠️ No 'Would You Rather' questions available right now.")

    @commands.command(name="fact")
    @command_error_handler
    async def fact(self, ctx):
        facts = self.get_data("facts")
        if facts:
            await ctx.send(f"🌟 Fun Fact: {random.choice(facts)}")
        else:
            await ctx.send("⚠️ No fun facts available right now.")

    @commands.command(name="reloadfun", hidden=True)
    @commands.is_owner()
    @command_error_handler
    async def reload_fun_data(self, ctx):
        self.data = load_fun_data()
        await ctx.send("🔄 Fun data has been reloaded!")

    @commands.command()
    async def triggered(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        avatar_url = member.avatar.url

        async with ctx.typing():
            try:
                response = requests.get(avatar_url)
                avatar = Image.open(io.BytesIO(response.content))

                avatar = avatar.resize((256, 256))

                base = Image.new("RGB", (256, 310), "black")
                base.paste(avatar, (0, 0))

                draw = ImageDraw.Draw(base)
                font = ImageFont.truetype("arial.ttf", 30)
                draw.rectangle([(0, 256), (256, 310)], fill="red")
                draw.text((64, 270), "TRIGGERED", font=font, fill="white")

                frames = []
                for _ in range(10):  # 10 frames
                    offset_x = random.randint(-10, 10)
                    offset_y = random.randint(-10, 10)
                    frame = Image.new("RGB", (256, 310), "black")
                    frame.paste(base, (offset_x, offset_y))
                    frames.append(frame)

                gif_bytes = io.BytesIO()
                frames[0].save(
                    gif_bytes,
                    format="GIF",
                    save_all=True,
                    append_images=frames[1:],
                    loop=0,
                    duration=50,
                )
                gif_bytes.seek(0)

                await ctx.send(file=discord.File(fp=gif_bytes, filename="triggered.gif"))
            except Exception as e:
                await ctx.send(f"⚠️ An error occurred: {e}")
    
    @commands.command(name="lgbtq")
    async def lgbtq(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        avatar_url = member.avatar.url

        async with ctx.typing():
            try:
                response = requests.get(avatar_url)
                avatar = Image.open(io.BytesIO(response.content)).convert("RGBA")

                avatar = avatar.resize((512, 512))

                flag_colors = [
                    (244, 67, 54),   # Red
                    (255, 152, 0),   # Orange
                    (255, 235, 59),  # Yellow
                    (76, 175, 80),   # Green
                    (33, 150, 243),  # Blue
                    (156, 39, 176),  # Purple
                ]
                flag_height = avatar.height // len(flag_colors)
                flag_overlay = Image.new("RGBA", avatar.size, (0, 0, 0, 0))

                for i, color in enumerate(flag_colors):
                    y_start = i * flag_height
                    y_end = (i + 1) * flag_height
                    draw = ImageDraw.Draw(flag_overlay)
                    draw.rectangle([(0, y_start), (avatar.width, y_end)], fill=color + (120,))  # Semi-transparent

                combined = Image.alpha_composite(avatar, flag_overlay)

                result_bytes = io.BytesIO()
                combined.save(result_bytes, format="PNG")
                result_bytes.seek(0)

                await ctx.send(file=discord.File(result_bytes, filename="lgbtq_avatar.png"))
            except Exception as e:
                await ctx.send(f"⚠️ An error occurred: {e}")

async def setup(bot):
    try:
        await bot.add_cog(FunCommands(bot))
    except commands.CommandRegistrationError as e:
        print(f"⚠️ Command registration error in `fun.py`: {e}")
    except Exception as e:
        print(f"⚠️ Failed to load `FunCommands` cog: {e}")