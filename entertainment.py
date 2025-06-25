
import discord
from discord.ext import commands
import random
import aiohttp
import asyncio

class Entertainment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.eight_ball_responses = [
            "Es seguro", "Es cierto", "Sin duda", "Sí definitivamente",
            "Puedes confiar en ello", "Como yo lo veo, sí", "Probablemente",
            "Las perspectivas son buenas", "Sí", "Las señales apuntan a que sí",
            "Respuesta confusa, intenta de nuevo", "Pregunta de nuevo más tarde",
            "Mejor no decirte ahora", "No puedo predecir ahora",
            "Concéntrate y pregunta de nuevo", "No cuentes con ello",
            "Mi respuesta es no", "Mis fuentes dicen que no",
            "Las perspectivas no son tan buenas", "Muy dudoso"
        ]
        
        self.jokes = [
            "¿Por qué los programadores prefieren el modo oscuro? Porque la luz atrae bugs! 🐛",
            "¿Cómo llamas a un desarrollador que no toma café? Un programador descafeinado! ☕",
            "¿Por qué los robots nunca entran en pánico? Porque tienen nervios de acero! 🤖",
            "¿Qué le dijo un array al otro? Nos vemos en el índice! 📊",
            "¿Por qué HTML y CSS rompieron? Porque no tenían química! 💔"
        ]
    
    @commands.hybrid_command(name="8ball", description="Pregunta a la bola mágica 8")
    async def eight_ball(self, ctx, *, question: str):
        if not question.endswith('?'):
            await ctx.send("❓ ¡Las preguntas deben terminar con signo de interrogación!")
            return
        
        response = random.choice(self.eight_ball_responses)
        
        embed = discord.Embed(
            title="🎱 Bola Mágica 8",
            color=0x000000
        )
        embed.add_field(name="Pregunta", value=question, inline=False)
        embed.add_field(name="Respuesta", value=f"*{response}*", inline=False)
        embed.set_footer(text=f"Preguntado por {ctx.author.display_name}")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="joke", description="Cuenta un chiste aleatorio")
    async def tell_joke(self, ctx):
        joke = random.choice(self.jokes)
        
        embed = discord.Embed(
            title="😄 Chiste del Día",
            description=joke,
            color=0xffff00
        )
        embed.set_footer(text="¡Espero que te haya gustado!")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="coinflip", description="Lanza una moneda")
    async def coinflip(self, ctx):
        result = random.choice(["Cara", "Cruz"])
        emoji = "🪙" if result == "Cara" else "⚡"
        
        embed = discord.Embed(
            title="🪙 Lanzamiento de Moneda",
            description=f"{emoji} **{result}**",
            color=0xffd700
        )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="dice", description="Lanza un dado")
    async def roll_dice(self, ctx, sides: int = 6):
        if sides < 2 or sides > 100:
            await ctx.send("❌ El dado debe tener entre 2 y 100 caras.")
            return
        
        result = random.randint(1, sides)
        
        embed = discord.Embed(
            title="🎲 Lanzamiento de Dado",
            description=f"**{result}** (de {sides} caras)",
            color=0xff6b6b
        )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="poll", description="Crear una encuesta")
    async def create_poll(self, ctx, question: str, *options):
        if len(options) < 2:
            await ctx.send("❌ Necesitas al menos 2 opciones para la encuesta.")
            return
        
        if len(options) > 10:
            await ctx.send("❌ Máximo 10 opciones permitidas.")
            return
        
        embed = discord.Embed(
            title="📊 Encuesta",
            description=question,
            color=0x00ff00
        )
        
        reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        
        for i, option in enumerate(options):
            embed.add_field(
                name=f"{reactions[i]} Opción {i+1}",
                value=option,
                inline=False
            )
        
        embed.set_footer(text=f"Encuesta creada por {ctx.author.display_name}")
        
        message = await ctx.send(embed=embed)
        
        for i in range(len(options)):
            await message.add_reaction(reactions[i])

async def setup(bot):
    await bot.add_cog(Entertainment(bot))
