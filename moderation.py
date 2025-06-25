
import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warns = {}  # Temporal, en producción usar DB
    
    @commands.hybrid_command(name="warn", description="Advertir a un usuario")
    @commands.has_permissions(manage_messages=True)
    async def warn_user(self, ctx, member: discord.Member, *, reason="No especificado"):
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)
        
        if guild_id not in self.warns:
            self.warns[guild_id] = {}
        if user_id not in self.warns[guild_id]:
            self.warns[guild_id][user_id] = []
        
        warn_data = {
            "reason": reason,
            "moderator": ctx.author.name,
            "timestamp": datetime.now().isoformat()
        }
        
        self.warns[guild_id][user_id].append(warn_data)
        
        embed = discord.Embed(
            title="⚠️ Usuario Advertido",
            description=f"{member.mention} ha sido advertido",
            color=0xffaa00
        )
        embed.add_field(name="Razón", value=reason, inline=False)
        embed.add_field(name="Moderador", value=ctx.author.mention, inline=True)
        embed.add_field(name="Advertencias totales", 
                       value=len(self.warns[guild_id][user_id]), inline=True)
        
        await ctx.send(embed=embed)
        
        try:
            await member.send(f"Has sido advertido en **{ctx.guild.name}**\nRazón: {reason}")
        except:
            pass
    
    @commands.hybrid_command(name="warnings", description="Ver advertencias de un usuario")
    async def check_warnings(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)
        
        user_warns = self.warns.get(guild_id, {}).get(user_id, [])
        
        if not user_warns:
            await ctx.send(f"{member.display_name} no tiene advertencias.")
            return
        
        embed = discord.Embed(
            title=f"⚠️ Advertencias de {member.display_name}",
            color=0xff0000
        )
        
        for i, warn in enumerate(user_warns[-5:], 1):  # Últimas 5
            embed.add_field(
                name=f"Advertencia #{i}",
                value=f"**Razón:** {warn['reason']}\n**Moderador:** {warn['moderator']}\n**Fecha:** {warn['timestamp'][:10]}",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="mute", description="Silenciar a un usuario")
    @commands.has_permissions(manage_messages=True)
    async def mute_user(self, ctx, member: discord.Member, duration: int = 10, *, reason="No especificado"):
        try:
            await member.timeout(timedelta(minutes=duration), reason=reason)
            
            embed = discord.Embed(
                title="🔇 Usuario Silenciado",
                description=f"{member.mention} ha sido silenciado por {duration} minutos",
                color=0xff0000
            )
            embed.add_field(name="Razón", value=reason, inline=False)
            embed.add_field(name="Moderador", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Error al silenciar: {e}")
    
    @commands.hybrid_command(name="unmute", description="Quitar silencio a un usuario")
    @commands.has_permissions(manage_messages=True)
    async def unmute_user(self, ctx, member: discord.Member):
        try:
            await member.timeout(None)
            await ctx.send(f"🔊 {member.mention} ya no está silenciado.")
        except Exception as e:
            await ctx.send(f"❌ Error al quitar silencio: {e}")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
