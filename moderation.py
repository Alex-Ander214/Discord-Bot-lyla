
import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio
import json
import os
from logger import bot_logger

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warnings = {}
        self.load_warnings()
    
    def load_warnings(self):
        """Cargar advertencias desde archivo"""
        try:
            if os.path.exists('warnings.json'):
                with open('warnings.json', 'r') as f:
                    data = json.load(f)
                    # Convertir timestamps de string a datetime
                    for guild_id in data:
                        for user_id in data[guild_id]:
                            for warning in data[guild_id][user_id]:
                                if isinstance(warning['timestamp'], str):
                                    warning['timestamp'] = datetime.fromisoformat(warning['timestamp'])
                    self.warnings = data
        except Exception as e:
            bot_logger.error(f"Error cargando advertencias: {e}")
            self.warnings = {}
    
    def save_warnings(self):
        """Guardar advertencias en archivo"""
        try:
            # Convertir datetime a string para JSON
            data = {}
            for guild_id in self.warnings:
                data[guild_id] = {}
                for user_id in self.warnings[guild_id]:
                    data[guild_id][user_id] = []
                    for warning in self.warnings[guild_id][user_id]:
                        warn_copy = warning.copy()
                        warn_copy['timestamp'] = warning['timestamp'].isoformat()
                        data[guild_id][user_id].append(warn_copy)
            
            with open('warnings.json', 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            bot_logger.error(f"Error guardando advertencias: {e}")
    
    @commands.hybrid_command(name="kick", description="Expulsar un usuario")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="Sin razón especificada"):
        try:
            await member.kick(reason=reason)
            
            embed = discord.Embed(
                title="👢 Usuario Expulsado",
                description=f"{member.mention} ha sido expulsado del servidor.",
                color=0xff6b6b
            )
            embed.add_field(name="Razón", value=reason, inline=False)
            embed.add_field(name="Moderador", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            bot_logger.info(f"Usuario {member} expulsado por {ctx.author} - Razón: {reason}")
            
        except Exception as e:
            await ctx.send(f"❌ Error al expulsar usuario: {e}")
    
    @commands.hybrid_command(name="ban", description="Banear un usuario")
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
            
        except Exception as e:
            await ctx.send(f"❌ Error al banear usuario: {e}")
    
    @commands.hybrid_command(name="timeout", description="Silenciar temporalmente un usuario")
    @commands.has_permissions(manage_messages=True)
    async def timeout(self, ctx, member: discord.Member, duration: int = 10, *, reason="Sin razón especificada"):
        try:
            await member.timeout(timedelta(minutes=duration), reason=reason)
            
            embed = discord.Embed(
                title="🔇 Usuario Silenciado",
                description=f"{member.mention} ha sido silenciado temporalmente.",
                color=0xffa500
            )
            embed.add_field(name="Duración", value=f"{duration} minutos", inline=True)
            embed.add_field(name="Razón", value=reason, inline=False)
            embed.add_field(name="Moderador", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            bot_logger.info(f"Usuario {member} silenciado por {duration} minutos por {ctx.author}")
            
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
        
        self.save_warnings()
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
                await member.timeout(timedelta(hours=1), 
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
    
    @commands.hybrid_command(name="clear_warnings", description="Limpiar advertencias de un usuario")
    @commands.has_permissions(administrator=True)
    async def clear_warnings(self, ctx, member: discord.Member):
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)
        
        if guild_id in self.warnings and user_id in self.warnings[guild_id]:
            del self.warnings[guild_id][user_id]
            self.save_warnings()
            await ctx.send(f"✅ Advertencias de {member.display_name} han sido limpiadas.")
        else:
            await ctx.send(f"{member.display_name} no tiene advertencias.")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
