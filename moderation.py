
import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio
from logger import bot_logger

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warnings = {}  # Almacenar advertencias temporalmente
    
    @commands.hybrid_command(name="kick", description="Expulsar a un usuario")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="Sin razón especificada"):
        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                title="👢 Usuario Expulsado",
                description=f"{member.mention} ha sido expulsado del servidor.",
                color=0xff9900
            )
            embed.add_field(name="Razón", value=reason, inline=False)
            embed.add_field(name="Moderador", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)
            bot_logger.info(f"Usuario {member} expulsado por {ctx.author} - Razón: {reason}")
        except discord.Forbidden:
            await ctx.send("❌ No tengo permisos para expulsar a este usuario.")
        except Exception as e:
            await ctx.send(f"❌ Error al expulsar usuario: {e}")
    
    @commands.hybrid_command(name="ban", description="Banear a un usuario")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="Sin razón especificada"):
        try:
            await member.ban(reason=reason)
            embed = discord.Embed(
                title="🔨 Usuario Baneado",
                description=f"{member.mention} ha sido baneado del servidor.",
                color=0xff0000
            )
            embed.add_field(name="Razón", value=reason, inline=False)
            embed.add_field(name="Moderador", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)
            bot_logger.info(f"Usuario {member} baneado por {ctx.author} - Razón: {reason}")
        except discord.Forbidden:
            await ctx.send("❌ No tengo permisos para banear a este usuario.")
        except Exception as e:
            await ctx.send(f"❌ Error al banear usuario: {e}")
    
    @commands.hybrid_command(name="unban", description="Desbanear a un usuario")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int, *, reason="Sin razón especificada"):
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user, reason=reason)
            embed = discord.Embed(
                title="✅ Usuario Desbaneado",
                description=f"{user.mention} ha sido desbaneado.",
                color=0x00ff00
            )
            embed.add_field(name="Razón", value=reason, inline=False)
            embed.add_field(name="Moderador", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)
            bot_logger.info(f"Usuario {user} desbaneado por {ctx.author} - Razón: {reason}")
        except discord.NotFound:
            await ctx.send("❌ Usuario no encontrado o no está baneado.")
        except Exception as e:
            await ctx.send(f"❌ Error al desbanear usuario: {e}")
    
    @commands.hybrid_command(name="timeout", description="Silenciar temporalmente a un usuario")
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, minutes: int, *, reason="Sin razón especificada"):
        try:
            if minutes > 10080:  # Máximo 7 días
                await ctx.send("❌ El tiempo máximo es 10080 minutos (7 días).")
                return
            
            until = discord.utils.utcnow() + timedelta(minutes=minutes)
            await member.timeout(until, reason=reason)
            
            embed = discord.Embed(
                title="🔇 Usuario Silenciado",
                description=f"{member.mention} ha sido silenciado por {minutes} minutos.",
                color=0xffaa00
            )
            embed.add_field(name="Razón", value=reason, inline=False)
            embed.add_field(name="Moderador", value=ctx.author.mention, inline=True)
            embed.add_field(name="Hasta", value=f"<t:{int(until.timestamp())}:F>", inline=True)
            await ctx.send(embed=embed)
            bot_logger.info(f"Usuario {member} silenciado por {ctx.author} - {minutes} minutos")
        except discord.Forbidden:
            await ctx.send("❌ No tengo permisos para silenciar a este usuario.")
        except Exception as e:
            await ctx.send(f"❌ Error al silenciar usuario: {e}")
    
    @commands.hybrid_command(name="warn", description="Advertir a un usuario")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason="Sin razón especificada"):
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)
        
        if guild_id not in self.warnings:
            self.warnings[guild_id] = {}
        if user_id not in self.warnings[guild_id]:
            self.warnings[guild_id][user_id] = []
        
        self.warnings[guild_id][user_id].append({
            "reason": reason,
            "moderator": str(ctx.author.id),
            "timestamp": datetime.now()
        })
        
        warning_count = len(self.warnings[guild_id][user_id])
        
        embed = discord.Embed(
            title="⚠️ Usuario Advertido",
            description=f"{member.mention} ha recibido una advertencia.",
            color=0xffff00
        )
        embed.add_field(name="Razón", value=reason, inline=False)
        embed.add_field(name="Moderador", value=ctx.author.mention, inline=True)
        embed.add_field(name="Advertencias totales", value=f"{warning_count}/3", inline=True)
        
        await ctx.send(embed=embed)
        
        # Auto-acción si alcanza 3 advertencias
        if warning_count >= 3:
            try:
                await member.timeout(discord.utils.utcnow() + timedelta(hours=1), 
                                   reason="3 advertencias alcanzadas - Timeout automático")
                await ctx.send(f"🔇 {member.mention} ha sido silenciado automáticamente por acumular 3 advertencias.")
            except:
                pass
    
    @commands.hybrid_command(name="warnings", description="Ver advertencias de un usuario")
    async def warnings(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)
        
        if guild_id not in self.warnings or user_id not in self.warnings[guild_id]:
            await ctx.send(f"{member.display_name} no tiene advertencias.")
            return
        
        user_warnings = self.warnings[guild_id][user_id]
        
        embed = discord.Embed(
            title=f"⚠️ Advertencias de {member.display_name}",
            description=f"Total: {len(user_warnings)} advertencias",
            color=0xffff00
        )
        
        for i, warning in enumerate(user_warnings[-5:], 1):  # Últimas 5
            moderator = ctx.guild.get_member(int(warning["moderator"]))
            mod_name = moderator.display_name if moderator else "Moderador desconocido"
            
            embed.add_field(
                name=f"Advertencia #{i}",
                value=f"**Razón:** {warning['reason']}\n"
                      f"**Moderador:** {mod_name}\n"
                      f"**Fecha:** {warning['timestamp'].strftime('%d/%m/%Y %H:%M')}",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="clear", description="Limpiar mensajes del canal")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 10):
        if amount > 100:
            await ctx.send("❌ No puedo borrar más de 100 mensajes a la vez.")
            return
        
        try:
            deleted = await ctx.channel.purge(limit=amount + 1)  # +1 para incluir el comando
            embed = discord.Embed(
                title="🧹 Mensajes Eliminados",
                description=f"Se eliminaron {len(deleted)-1} mensajes.",
                color=0x00ff00
            )
            msg = await ctx.send(embed=embed)
            await asyncio.sleep(3)
            await msg.delete()
            bot_logger.info(f"{ctx.author} eliminó {len(deleted)-1} mensajes en {ctx.channel}")
        except discord.Forbidden:
            await ctx.send("❌ No tengo permisos para eliminar mensajes.")
        except Exception as e:
            await ctx.send(f"❌ Error eliminando mensajes: {e}")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
