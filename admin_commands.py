
import discord
from discord.ext import commands
from config import ConfigManager

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = ConfigManager()
    
    @commands.hybrid_command(name="server_config", description="Ver configuración del servidor")
    @commands.has_permissions(administrator=True)
    async def server_config(self, ctx):
        config = self.config.get_config(str(ctx.guild.id))
        
        embed = discord.Embed(
            title="⚙️ Configuración del Servidor",
            color=0x7289da
        )
        
        embed.add_field(
            name="🛡️ Auto-moderación",
            value="✅ Activada" if config.auto_moderation else "❌ Desactivada",
            inline=True
        )
        
        embed.add_field(
            name="📝 Logging",
            value="✅ Activado" if config.logging_enabled else "❌ Desactivado",
            inline=True
        )
        
        embed.add_field(
            name="👋 Canal de bienvenida",
            value=f"<#{config.welcome_channel}>" if config.welcome_channel else "No configurado",
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="toggle_automod", description="Activar/desactivar auto-moderación")
    @commands.has_permissions(administrator=True)
    async def toggle_automod(self, ctx):
        config = self.config.get_config(str(ctx.guild.id))
        config.auto_moderation = not config.auto_moderation
        self.config.save_config(str(ctx.guild.id), config)
        
        status = "✅ Activada" if config.auto_moderation else "❌ Desactivada"
        await ctx.send(f"Auto-moderación: {status}")
    
    @commands.hybrid_command(name="toggle_logging", description="Activar/desactivar logging")
    @commands.has_permissions(administrator=True)
    async def toggle_logging(self, ctx):
        config = self.config.get_config(str(ctx.guild.id))
        config.logging_enabled = not config.logging_enabled
        self.config.save_config(str(ctx.guild.id), config)
        
        status = "✅ Activado" if config.logging_enabled else "❌ Desactivado"
        await ctx.send(f"Logging: {status}")
    
    @commands.hybrid_command(name="set_welcome", description="Configurar canal de bienvenida")
    @commands.has_permissions(administrator=True)
    async def set_welcome(self, ctx, channel: discord.TextChannel):
        self.config.update_config(str(ctx.guild.id), welcome_channel=str(channel.id))
        await ctx.send(f"✅ Canal de bienvenida configurado: {channel.mention}")
    
    @commands.hybrid_command(name="backup", description="Crear backup de configuración")
    @commands.has_permissions(administrator=True)
    async def backup_config(self, ctx):
        try:
            config = self.config.get_config(str(ctx.guild.id))
            backup_data = {
                "guild_id": ctx.guild.id,
                "config": config.__dict__,
                "timestamp": discord.utils.utcnow().isoformat()
            }
            
            await ctx.send("✅ Backup de configuración creado exitosamente.")
        except Exception as e:
            await ctx.send(f"❌ Error creando backup: {e}")
    
    @commands.hybrid_command(name="purge", description="Eliminar mensajes en masa")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int = 5):
        if amount > 100:
            await ctx.send("❌ No puedes eliminar más de 100 mensajes a la vez.")
            return
        
        try:
            deleted = await ctx.channel.purge(limit=amount + 1)  # +1 para incluir el comando
            await ctx.send(f"✅ {len(deleted)-1} mensajes eliminados.", delete_after=5)
        except Exception as e:
            await ctx.send(f"❌ Error eliminando mensajes: {e}")
    
    @commands.hybrid_command(name="role_add", description="Añadir rol a un usuario")
    @commands.has_permissions(manage_roles=True)
    async def role_add(self, ctx, member: discord.Member, role: discord.Role):
        try:
            await member.add_roles(role)
            await ctx.send(f"✅ Rol {role.mention} añadido a {member.mention}")
        except Exception as e:
            await ctx.send(f"❌ Error añadiendo rol: {e}")
    
    @commands.hybrid_command(name="role_remove", description="Quitar rol de un usuario")
    @commands.has_permissions(manage_roles=True)
    async def role_remove(self, ctx, member: discord.Member, role: discord.Role):
        try:
            await member.remove_roles(role)
            await ctx.send(f"✅ Rol {role.mention} removido de {member.mention}")
        except Exception as e:
            await ctx.send(f"❌ Error removiendo rol: {e}")

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
