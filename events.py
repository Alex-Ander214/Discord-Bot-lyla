
import discord
from discord.ext import commands
from logger import bot_logger

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        bot_logger.info(f"Bot añadido al servidor: {guild.name} (ID: {guild.id})")
        
        # Buscar canal general para mensaje de bienvenida
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                embed = discord.Embed(
                    title="👋 ¡Hola! Soy Lyla",
                    description="Gracias por añadirme a tu servidor. Usa `/config` para configurarme.",
                    color=0x00ff00
                )
                embed.add_field(
                    name="🚀 Primeros Pasos",
                    value="• Usa `/set_chatbot #canal` para configurar donde responderé\n"
                          "• Usa `/config` para ver todas las opciones\n"
                          "• Usa `/help` para ver todos mis comandos",
                    inline=False
                )
                await channel.send(embed=embed)
                break
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        bot_logger.info(f"Bot removido del servidor: {guild.name} (ID: {guild.id})")
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Sistema de bienvenida automática
        from config import ConfigManager
        config_manager = ConfigManager()
        config = config_manager.get_config(str(member.guild.id))
        
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
                    await channel.send(embed=embed)
            except Exception as e:
                bot_logger.error(f"Error enviando mensaje de bienvenida: {e}")
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ No tienes permisos para usar este comando.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ Comando en cooldown. Espera {error.retry_after:.1f} segundos.")
        else:
            bot_logger.error(f"Error en comando {ctx.command}: {error}")
            await ctx.send("❌ Ocurrió un error inesperado.")

async def setup(bot):
    await bot.add_cog(Events(bot))
