import discord
from discord.ext import commands
from logger import bot_logger
from config import ConfigManager

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = ConfigManager()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Evento cuando el bot se une a un servidor"""
        bot_logger.info(f"Bot se unió al servidor: {guild.name} (ID: {guild.id})")

        # Buscar canal general para enviar mensaje de bienvenida
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                embed = discord.Embed(
                    title="¡Hola! Soy Lyla 🤖",
                    description="Gracias por agregarme a tu servidor. Usa `/info` para conocer más sobre mí.",
                    color=0x00ff00
                )
                embed.add_field(
                    name="Configuración",
                    value="Usa `/set_chatbot` para configurar un canal donde responderé automáticamente.",
                    inline=False
                )
                await channel.send(embed=embed)
                break

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """Evento cuando el bot es removido de un servidor"""
        bot_logger.info(f"Bot removido del servidor: {guild.name} (ID: {guild.id})")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Manejo global de errores"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Faltan argumentos requeridos para este comando.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ No tienes permisos para usar este comando.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ No tengo los permisos necesarios para ejecutar este comando.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ Este comando está en cooldown. Intenta de nuevo en {error.retry_after:.1f} segundos.")
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