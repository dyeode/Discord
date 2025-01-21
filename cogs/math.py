import discord
from discord.ext import commands
from sympy import Eq, solve, symbols, integrate, diff, limit, Matrix

class AdvancedMath(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def differentiate(self, ctx, *, expression: str):
        try:
            x = symbols('x')
            result = diff(expression, x)
            await ctx.send(result)
        except Exception as e:
            await ctx.send(f"⚠️ Could not differentiate the expression. Error: {e}")

    @commands.command()
    async def integrate(self, ctx, *, expression: str):
        try:
            x = symbols('x')
            result = integrate(expression, x)
            await ctx.send(f"{result} + C")
        except Exception as e:
            await ctx.send(f"⚠️ Could not integrate the expression. Error: {e}")

    @commands.command()
    async def definite_integral(self, ctx, lower: float, upper: float, *, expression: str):
        try:
            x = symbols('x')
            result = integrate(expression, (x, lower, upper))
            await ctx.send(result)
        except Exception as e:
            await ctx.send(f"⚠️ Could not calculate the definite integral. Error: {e}")

    @commands.command()
    async def limit(self, ctx, point: float, *, expression: str):
        try:
            x = symbols('x')
            result = limit(expression, x, point)
            await ctx.send(result)
        except Exception as e:
            await ctx.send(f"⚠️ Could not calculate the limit. Error: {e}")

    @commands.command()
    async def matrix_add(self, ctx, *, matrices: str):
        try:
            matrix_a, matrix_b = matrices.split("+")
            matrix_a = Matrix(eval(matrix_a.strip()))
            matrix_b = Matrix(eval(matrix_b.strip()))
            result = matrix_a + matrix_b
            await ctx.send(result)
        except Exception as e:
            await ctx.send(f"⚠️ Could not add the matrices. Error: {e}")

    @commands.command()
    async def matrix_multiply(self, ctx, *, matrices: str):
        try:
            matrix_a, matrix_b = matrices.split("*")
            matrix_a = Matrix(eval(matrix_a.strip()))
            matrix_b = Matrix(eval(matrix_b.strip()))
            result = matrix_a * matrix_b
            await ctx.send(result)
        except Exception as e:
            await ctx.send(f"⚠️ Could not multiply the matrices. Error: {e}")
    
    @commands.command()
    async def determinant(self, ctx, *, matrix: str):
        try:
            matrix = Matrix(eval(matrix))
            result = matrix.det()
            await ctx.send(result)
        except Exception as e:
            await ctx.send(f"⚠️ Could not calculate the determinant. Error: {e}")
    
    @commands.command()
    async def transpose(self, ctx, *, matrix: str):
        try:
            matrix = Matrix(eval(matrix))
            result = matrix.T
            await ctx.send(result)
        except Exception as e:
            await ctx.send(f"⚠️ Could not calculate the transpose. Error: {e}")

async def setup(bot):
    await bot.add_cog(AdvancedMath(bot))