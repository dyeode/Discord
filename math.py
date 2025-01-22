import discord
from discord.ext import commands
from sympy import Eq, solve, symbols, integrate, diff, limit, Matrix
from functools import wraps
from ast import literal_eval

async def setup(bot):
    try:
        await bot.add_cog(AdvancedMath(bot))
    except Exception as e:
        print(f"⚠️ Failed to load `AdvancedMath` cog: {e}")

def get_symbol(name: str = 'x'):
    return symbols(name)

def math_command_handler(func):
    @wraps(func)
    async def wrapper(self, ctx, *args, **kwargs):
        try:
            await func(self, ctx, *args, **kwargs)
        except Exception as e:
            await ctx.send(f"⚠️ An error occurred: {e}")
    return wrapper

def parse_matrix(matrix_str: str):
    try:
        matrix_data = literal_eval(matrix_str.strip())
        return Matrix(matrix_data)
    except (ValueError, SyntaxError):
        raise ValueError("Invalid matrix input. Ensure it's in the correct format.")

class AdvancedMath(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @math_command_handler
    async def differentiate(self, ctx, *, expression: str):
        x = get_symbol()
        result = diff(expression, x)
        await ctx.send(result)

    @commands.command()
    @math_command_handler
    async def integrate(self, ctx, *, expression: str):
        x = get_symbol()
        result = integrate(expression, x)
        await ctx.send(f"{result} + C")

    @commands.command()
    @math_command_handler
    async def definite_integral(self, ctx, lower: float, upper: float, *, expression: str):
        x = get_symbol()
        result = integrate(expression, (x, lower, upper))
        await ctx.send(result)

    @commands.command()
    @math_command_handler
    async def limit(self, ctx, point: float, *, expression: str):
        x = get_symbol()
        result = limit(expression, x, point)
        await ctx.send(result)

    @commands.command()
    @math_command_handler
    async def matrix_add(self, ctx, *, matrices: str):
        matrix_a, matrix_b = matrices.split("+")
        result = parse_matrix(matrix_a) + parse_matrix(matrix_b)
        await ctx.send(result)

    @commands.command()
    @math_command_handler
    async def matrix_multiply(self, ctx, *, matrices: str):
        matrix_a, matrix_b = matrices.split("*")
        result = parse_matrix(matrix_a) * parse_matrix(matrix_b)
        await ctx.send(result)

    @commands.command()
    @math_command_handler
    async def determinant(self, ctx, *, matrix: str):
        result = parse_matrix(matrix).det()
        await ctx.send(result)

    @commands.command()
    @math_command_handler
    async def transpose(self, ctx, *, matrix: str):
        result = parse_matrix(matrix).T
        await ctx.send(result)


async def setup(bot):
    await bot.add_cog(AdvancedMath(bot))