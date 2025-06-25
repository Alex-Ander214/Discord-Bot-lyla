
import discord
from discord.ext import commands
from config import ConfigManager

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = ConfigManager()
    
    @commands.hybrid_command(name="config", description="Configurar el bot para este servidor")
    @commands.has_permissions(administrator=True)
    async def server_config(self, ctx):
        embed = discord.Embed(
            title="⚙️ Configuración del Servidor",
            description="Usa los siguientes comandos para configurar el bot:",
            color=0x00ff00
        )
        
        config = self.config.get_config(str(ctx.guild.id))
        
        embed.add_field(
            name="📝 Comandos Disponibles",
            value=f"`/set_prefix` - Cambiar prefijo (actual: {config.prefix})\n"
                  f"`/set_welcome` - Canal de bienvenida\n"
                  f"`/set_logs` - Canal de logs\n"
                  f"`/toggle_automod` - Auto moderación\n"
                  f"`/set_autorole` - Rol automático",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="set_prefix", description="Cambiar prefijo del bot")
    @commands.has_permissions(administrator=True)
    async def set_prefix(self, ctx, prefix: str):
        if len(prefix) > 3:
            await ctx.send("❌ El prefijo no puede tener más de 3 caracteres.")
            return
        
        self.config.update_config(str(ctx.guild.id), prefix=prefix)
        await ctx.send(f"✅ Prefijo cambiado a: `{prefix}`")
    
    @commands.hybrid_command(name="set_welcome", description="Configurar canal de bienvenida")
    @commands.has_permissions(administrator=True)
    async def set_welcome(self, ctx, channel: discord.TextChannel):
        self.config.update_config(str(ctx.guild.id), welcome_channel=str(channel.id))
        await ctx.send(f"✅ Canal de bienvenida configurado: {channel.mention}")
    
    @commands.hybrid_command(name="backup", description="Crear backup de configuración")
    @commands.has_permissions(administrator=True)
    async def backup_config(self, ctx):
        from database import BotDatabase
        
        if not hasattr(self.bot, 'db') or not self.bot.db:
            await ctx.send("❌ Base de datos no disponible")
            return
        
        try:
            # Crear backup en MongoDB
            backup_data = {
                "guild_id": ctx.guild.id,
                "config": self.config.get_config(str(ctx.guild.id)).__dict__,
                "timestamp": discord.utils.utcnow()
            }
            
            await ctx.send("✅ Backup de configuración creado exitosamente.")
        except Exception as e:
            await ctx.send(f"❌ Error creando backup: {e}")

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
