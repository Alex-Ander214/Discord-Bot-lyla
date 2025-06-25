
import discord
from discord.ext import commands
import random
import aiohttp
import json

class Entertainment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="roll", description="Lanzar un dado")
    async def roll(self, ctx, sides: int = 6):
        if sides < 2 or sides > 100:
            await ctx.send("❌ El dado debe tener entre 2 y 100 caras.")
            return
        
        result = random.randint(1, sides)
        embed = discord.Embed(
            title="🎲 Lanzamiento de Dado",
            description=f"**Resultado:** {result} (d{sides})",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="coinflip", description="Lanzar una moneda")
    async def coinflip(self, ctx):
        result = random.choice(["Cara", "Cruz"])
        emoji = "🪙" if result == "Cara" else "🔄"
        
        embed = discord.Embed(
            title=f"{emoji} Lanzamiento de Moneda",
            description=f"**Resultado:** {result}",
            color=0xffd700
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="8ball", description="Pregunta a la bola 8")
    async def eight_ball(self, ctx, *, question: str):
        responses = [
            "Es cierto", "Es decididamente así", "Sin duda",
            "Sí, definitivamente", "Puedes confiar en ello",
            "Como yo lo veo, sí", "Muy probable", "Perspectiva buena",
            "Las señales apuntan que sí", "Sí", "Respuesta confusa, intenta de nuevo",
            "Pregunta de nuevo más tarde", "Mejor no te lo digo ahora",
            "No puedo predecir ahora", "Concéntrate y pregunta de nuevo",
            "No cuentes con ello", "Mi respuesta es no",
            "Mis fuentes dicen que no", "Perspectiva no muy buena", "Muy dudoso"
        ]
        
        response = random.choice(responses)
        
        embed = discord.Embed(
            title="🎱 Bola 8 Mágica",
            color=0x800080
        )
        embed.add_field(name="Pregunta", value=question, inline=False)
        embed.add_field(name="Respuesta", value=response, inline=False)
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="joke", description="Contar un chiste")
    async def joke(self, ctx):
        jokes = [
            "¿Por qué los programadores prefieren el modo oscuro? Porque la luz atrae bugs.",
            "¿Cuál es el colmo de un programador? Que su mujer le diga que tiene un bug.",
            "¿Por qué los programadores no pueden contar hasta 31 en octubre? Porque después del 30 viene el 00.",
            "¿Cómo se llama un programador que no programa? Comentario.",
            "¿Qué le dice un bit al otro? Nos vemos en el bus.",
            "¿Por qué los programadores odian la naturaleza? Porque tiene demasiados bugs.",
            "¿Cuántos programadores se necesitan para cambiar una bombilla? Ninguno, es un problema de hardware."
        ]
        
        joke = random.choice(jokes)
        
        embed = discord.Embed(
            title="😂 Chiste del Día",
            description=joke,
            color=0xffff00
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="choose", description="Elegir entre opciones")
    async def choose(self, ctx, *, options: str):
        choices = [choice.strip() for choice in options.split(",")]
        
        if len(choices) < 2:
            await ctx.send("❌ Necesitas al menos 2 opciones separadas por comas.")
            return
        
        choice = random.choice(choices)
        
        embed = discord.Embed(
            title="🤔 Elección Aleatoria",
            description=f"**He elegido:** {choice}",
            color=0x00ffff
        )
        embed.add_field(name="Opciones", value=", ".join(choices), inline=False)
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="meme", description="Obtener un meme aleatorio")
    async def meme(self, ctx):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://meme-api.com/gimme") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        embed = discord.Embed(
                            title=data.get("title", "Meme Aleatorio"),
                            color=0xff69b4
                        )
                        embed.set_image(url=data.get("url"))
                        embed.set_footer(text=f"👍 {data.get('ups', 0)} upvotes")
                        
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send("❌ No pude obtener un meme en este momento.")
        except Exception as e:
            await ctx.send("❌ Error obteniendo meme. Intenta más tarde.")

async def setup(bot):
    await bot.add_cog(Entertainment(bot))
