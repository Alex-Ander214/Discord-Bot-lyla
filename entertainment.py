import discord
from discord.ext import commands
import random
import aiohttp
import json

class Entertainment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="dado", description="Lanza un dado de 6 caras")
    async def roll_dice(self, ctx):
        """Lanza un dado"""
        result = random.randint(1, 6)
        embed = discord.Embed(
            title="🎲 Lanzamiento de Dado",
            description=f"Has obtenido: **{result}**",
            color=0x00ff00
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="moneda", description="Lanza una moneda")
    async def flip_coin(self, ctx):
        """Lanza una moneda"""
        result = random.choice(["Cara", "Cruz"])
        emoji = "🪙" if result == "Cara" else "🔄"
        embed = discord.Embed(
            title=f"{emoji} Lanzamiento de Moneda",
            description=f"Resultado: **{result}**",
            color=0xffd700
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="8ball", description="Pregunta a la bola mágica")
    async def eight_ball(self, ctx, *, pregunta: str):
        """Bola mágica 8"""
        respuestas = [
            "Es cierto", "Definitivamente sí", "Sin duda", "Sí, definitivamente",
            "Puedes confiar en ello", "Como yo lo veo, sí", "Lo más probable",
            "Las perspectivas son buenas", "Sí", "Las señales apuntan a que sí",
            "Respuesta confusa, intenta de nuevo", "Pregunta de nuevo más tarde",
            "Mejor no decírtelo ahora", "No puedo predecirlo ahora",
            "Concéntrate y pregunta de nuevo", "No cuentes con ello",
            "Mi respuesta es no", "Mis fuentes dicen que no",
            "Las perspectivas no son tan buenas", "Muy dudoso"
        ]
        respuesta = random.choice(respuestas)
        embed = discord.Embed(
            title="🎱 Bola Mágica 8",
            description=f"**Pregunta:** {pregunta}\n**Respuesta:** {respuesta}",
            color=0x800080
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="chiste", description="Cuenta un chiste aleatorio")
    async def joke(self, ctx):
        """Cuenta un chiste"""
        chistes = [
            "¿Por qué los pájaros vuelan hacia el sur en invierno? Porque es muy lejos para caminar.",
            "¿Qué le dice un iguana a su hermana gemela? Somos iguanitas.",
            "¿Cómo se llama el campeón de buceo japonés? Tokofondo.",
            "¿Qué hace una abeja en el gimnasio? ¡Zum-ba!",
            "¿Por qué los peces no pagan impuestos? Porque viven en el agua y no en la tierra.",
            "¿Cómo se despiden los químicos? Ácido un placer.",
            "¿Qué le dice una impresora a otra? Esa hoja es tuya o es impresión mía.",
        ]
        chiste = random.choice(chistes)
        embed = discord.Embed(
            title="😂 Chiste del Día",
            description=chiste,
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