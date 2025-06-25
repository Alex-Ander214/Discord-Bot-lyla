
import discord
from discord.ext import commands
from config import ConfigManager
from logger import bot_logger

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = ConfigManager()
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Evento cuando un usuario se une al servidor"""
        config = self.config.get_config(str(member.guild.id))
        
        if config.welcome_channel:
            try:
                channel = member.guild.get_channel(int(config.welcome_channel))
                if channel:
                    embed = discord.Embed(
                        title="👋 ¡Bienvenido!",
                        description=f"¡Hola {member.mention}! Bienvenido a **{member.guild.name}**",
                        color=0x00ff00
                    )
                    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
                    embed.add_field(name="Miembro #", value=len(member.guild.members), inline=True)
                    embed.add_field(name="Cuenta creada", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
                    await channel.send(embed=embed)
            except Exception as e:
                bot_logger.error(f"Error enviando mensaje de bienvenida: {e}")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Evento cuando un usuario abandona el servidor"""
        config = self.config.get_config(str(member.guild.id))
        
        if config.welcome_channel:
            try:
                channel = member.guild.get_channel(int(config.welcome_channel))
                if channel:
                    embed = discord.Embed(
                        title="👋 Adiós",
                        description=f"{member.display_name} ha abandonado el servidor",
                        color=0xff6b6b
                    )
                    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
                    await channel.send(embed=embed)
            except Exception as e:
                bot_logger.error(f"Error enviando mensaje de despedida: {e}")
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Manejo global de errores de comandos"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ No tienes permisos para usar este comando.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ Comando en cooldown. Espera {error.retry_after:.1f} segundos.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Faltan argumentos requeridos: `{error.param.name}`")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Argumento inválido. Verifica el formato.")
        else:
            bot_logger.error(f"Error en comando {ctx.command}: {error}")
            await ctx.send("❌ Ocurrió un error inesperado.")
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Log de mensajes eliminados"""
        if message.author.bot:
            return
            
        config = self.config.get_config(str(message.guild.id))
        if config.logging_enabled:
            bot_logger.info(f"Mensaje eliminado en {message.guild.name} - {message.author}: {message.content[:100]}")
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Log de mensajes editados"""
        if before.author.bot or before.content == after.content:
            return
            
        config = self.config.get_config(str(before.guild.id))
        if config.logging_enabled:
            bot_logger.info(f"Mensaje editado en {before.guild.name} - {before.author}: '{before.content[:50]}' -> '{after.content[:50]}'")

async def setup(bot):
    await bot.add_cog(Events(bot))
