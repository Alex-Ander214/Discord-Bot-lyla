import aiohttp
import os
import io
import json
import re
import discord
import google.generativeai as genai
from discord.ext import commands
from discord import Embed, app_commands
from gasmii import text_model, image_model
from database import BotDatabase
from dotenv import load_dotenv

# Inicializar base de datos
try:
    db = BotDatabase()
    print("✅ Conexión a MongoDB establecida")
except Exception as e:
    print(f"❌ Error conectando a MongoDB: {e}")
    db = None

message_history = {}  # Mantenemos caché en memoria para rapidez
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents, heartbeat_timeout=60)
load_dotenv()

GOOGLE_AI_KEY = os.getenv("GOOGLE_AI_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
MAX_HISTORY = int(os.getenv("MAX_HISTORY"))

# Configuración de variables de entorno
if not GOOGLE_AI_KEY or not DISCORD_BOT_TOKEN:
    raise ValueError("Faltan variables de entorno requeridas: GOOGLE_AI_KEY y DISCORD_BOT_TOKEN")

@bot.event
async def on_ready():
    await bot.tree.sync()
    num_commands = len(bot.commands)
    invite_link = discord.utils.oauth_url(
        bot.user.id,
        permissions=discord.Permissions(),
        scopes=("bot", "applications.commands")
    )

    def print_in_color(text, color):
        return f"\033[{color}m{text}\033[0m"

    if os.name == 'posix':
        os.system('clear')
    elif os.name == 'nt':
        os.system('cls')

    ascii_art = """
    \033[1;35m
    
███████╗██████╗ ███████╗██╗  ██╗████████╗██████╗ ██╗   ██╗███╗   ███╗
██╔════╝██╔══██╗██╔════╝██║ ██╔╝╚══██╔══╝██╔══██╗██║   ██║████╗ ████║
███████╗██████╔╝█████╗  █████╔╝    ██║   ██████╔╝██║   ██║██╔████╔██║
╚════██║██╔═══╝ ██╔══╝  ██╔═██╗    ██║   ██╔══██╗██║   ██║██║╚██╔╝██║
███████║██║     ███████╗██║  ██╗   ██║   ██║  ██║╚██████╔╝██║ ╚═╝ ██║
╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝
                                                                     
\033[0m
    """

    print(ascii_art)
    print(print_in_color(f"{bot.user} aka {bot.user.name} ¡se ha conectado a Discord!", "\033[1;97"))
    print(print_in_color(f"  Cargado comandos: {num_commands} comandos exitosos", "1;35"))
    print(print_in_color(f"      Enlace de invitación: {invite_link}", "1;36"))


@bot.hybrid_command(name="reset", description="Borra el historial de mensajes del bot")
async def reset(ctx):
    global message_history
    user_id = ctx.author.id
    
    # Limpiar caché local
    if user_id in message_history:
        del message_history[user_id]
    
    # Limpiar base de datos
    if db:
        try:
            result = db.clear_user_history(user_id)
            await ctx.send(f"🤖 Historial borrado: {result.deleted_count} conversaciones eliminadas.")
        except Exception as e:
            await ctx.send(f"⚠️ Error al borrar historial: {e}")
    else:
        await ctx.send("🤖 El historial de mensajes del bot ha sido borrado (solo caché local).")

@bot.hybrid_command(name="info", description="Información sobre el bot")
async def info(ctx):
    embed = Embed(title="🤖 Información de Lyla", color=0x7289da)
    embed.add_field(name="📊 Servidores", value=len(bot.guilds), inline=True)
    embed.add_field(name="👥 Usuarios", value=sum(guild.member_count for guild in bot.guilds if guild.member_count), inline=True)
    embed.add_field(name="🏓 Latencia", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="🔗 Invitar", value="[Añadir a tu servidor](https://discord.com/oauth2/authorize?client_id=1387117751780245655&scope=bot+applications.commands&permissions=0)", inline=False)
    embed.add_field(name="🆘 Soporte", value="[Servidor de soporte](https://www.discord.gg/gkn2hxfTc7)", inline=False)
    embed.set_footer(text="Desarrollado por Alex")
    await ctx.send(embed=embed)

@bot.hybrid_command(name="stats", description="Estadísticas del bot y usuario")
async def stats(ctx):
    if not db:
        await ctx.send("❌ Base de datos no disponible")
        return
    
    try:
        global_stats = db.get_global_stats()
        user_stats = db.get_user_stats(ctx.author.id)
        
        embed = Embed(title="📊 Estadísticas", color=0x00ff00)
        embed.add_field(name="🌍 Global", 
                       value=f"Conversaciones: {global_stats['total_conversations']}\n"
                             f"Usuarios: {global_stats['total_users']}\n"
                             f"Servidores: {global_stats['total_servers']}", 
                       inline=True)
        embed.add_field(name="👤 Tu actividad", 
                       value=f"Mensajes: {user_stats['message_count']}\n"
                             f"Última actividad: {user_stats['last_active'].strftime('%d/%m/%Y') if user_stats['last_active'] else 'N/A'}", 
                       inline=True)
        
        if ctx.guild:
            server_stats = db.get_server_stats(ctx.guild.id)
            embed.add_field(name="🏠 Este servidor", 
                           value=f"Mensajes: {server_stats['server_messages']}\n"
                                 f"Usuarios activos: {server_stats['active_users']}", 
                           inline=True)
        
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Error obteniendo estadísticas: {e}")

    
def create_chatbot_channels_file():
    if not os.path.exists('chatbot_channels.json'):
        with open('chatbot_channels.json', 'w') as file:
            json.dump({}, file)

create_chatbot_channels_file()

chatbot_channels_file = 'chatbot_channels.json'
chatbot_channels = {}

# Load chatbot channels from chatbot_channels.json if it exists
if os.path.exists(chatbot_channels_file):
    with open(chatbot_channels_file, 'r') as file:
        chatbot_channels = json.load(file)

# Command to set or toggle chatbot channel
@bot.hybrid_command(name="set_chatbot", description="Configurar o alternar canal del chatbot")
async def set_chatbot(ctx, channel: discord.TextChannel):
    if ctx.guild is None:
        await ctx.send("Este comando solo puede usarse en un servidor.")
        return

    guild_id = str(ctx.guild.id)

    with open(chatbot_channels_file, 'r') as file:
        chatbot_channels = json.load(file)

    if guild_id in chatbot_channels:
        if chatbot_channels[guild_id]['channel_id'] == str(channel.id):
            del chatbot_channels[guild_id]
            await ctx.send(f"Las respuestas del chatbot han sido desactivadas para #{channel.name}.")
        else:
            chatbot_channels[guild_id] = {'channel_id': str(channel.id)}
            await ctx.send(f"Las respuestas del chatbot han sido configuradas para #{channel.name}.")
    else:
        chatbot_channels[guild_id] = {'channel_id': str(channel.id)}
        await ctx.send(f"Las respuestas del chatbot han sido configuradas para #{channel.name}.")

    with open(chatbot_channels_file, 'w') as file:
        json.dump(chatbot_channels, file, indent=4)

# Event handler for new messages
@bot.event
async def on_message(message):
    # Ignore messages sent by the bot
    if message.author == bot.user:
        return
    # Check if the bot is mentioned, the message is a DM, or it's in a designated chatbot channel
    guild_id = str(message.guild.id) if message.guild else None
    is_chatbot_channel = False

    if guild_id and guild_id in chatbot_channels:
        is_chatbot_channel = str(message.channel.id) == chatbot_channels[guild_id]['channel_id']

    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel) or is_chatbot_channel:
        #Start Typing to seem like something happened
        cleaned_text = clean_discord_message(message.content)

        async with message.channel.typing():
            # Check for image attachments
            if message.attachments:
                print("New Image Message FROM:" + str(message.author.id) + ": " + cleaned_text)
                #Currently no chat history for images
                for attachment in message.attachments:
                    #these are the only image extentions it currently accepts
                    if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                        await message.add_reaction('🎨')

                        async with aiohttp.ClientSession() as session:
                            async with session.get(attachment.url) as resp:
                                if resp.status != 200:
                                    await message.channel.send('No se pudo descargar la imagen.')
                                    return
                                image_data = await resp.read()
                                response_text = await generate_response_with_image_and_text(image_data, cleaned_text)
                                #Split the Message so discord does not get upset
                                await split_and_send_messages(message, response_text, 1700)
                                return
            #Not an Image do text response
            else:
                print("New Message FROM:" + str(message.author.id) + ": " + cleaned_text)
                #Check for Keyword Reset
                if "RESET" in cleaned_text or "REINICIAR" in cleaned_text.upper():
                    #End back message
                    if message.author.id in message_history:
                        del message_history[message.author.id]
                    await message.channel.send("🤖 Historial reiniciado para el usuario: " + str(message.author.name))
                    return
                await message.add_reaction('💬')

                # Actualizar estadísticas
                if db:
                    db.update_user_stats(message.author.id, message.guild.id if message.guild else None)
                    if message.guild:
                        db.update_server_stats(message.guild.id)
                
                #Check if history is disabled just send response
                if(MAX_HISTORY == 0):
                    response_text = await generate_response_with_text(cleaned_text)
                    # Guardar en DB sin historial
                    if db:
                        try:
                            db.save_message(message.author.id, cleaned_text, response_text, message.guild.id if message.guild else None)
                        except Exception as e:
                            print(f"Error guardando en DB: {e}")
                    await split_and_send_messages(message, response_text, 1700)
                    return;
                
                # Obtener historial (primero de DB, luego caché)
                if db:
                    try:
                        formatted_history = db.get_formatted_history(message.author.id, MAX_HISTORY)
                        if formatted_history:
                            response_text = await generate_response_with_text(formatted_history + "\n\n" + cleaned_text)
                        else:
                            response_text = await generate_response_with_text(cleaned_text)
                        
                        # Guardar conversación en DB
                        db.save_message(message.author.id, cleaned_text, response_text, message.guild.id if message.guild else None)
                    except Exception as e:
                        print(f"Error con MongoDB, usando caché local: {e}")
                        # Fallback al sistema anterior
                        update_message_history(message.author.id, cleaned_text)
                        response_text = await generate_response_with_text(get_formatted_message_history(message.author.id))
                        update_message_history(message.author.id, response_text)
                else:
                    # Sistema anterior como fallback
                    update_message_history(message.author.id, cleaned_text)
                    response_text = await generate_response_with_text(get_formatted_message_history(message.author.id))
                    update_message_history(message.author.id, response_text)
                
                await split_and_send_messages(message, response_text, 1700)


    

#ry-------------------------------------------------

async def generate_response_with_text(message_text):
    try:
        prompt_parts = [message_text]
        print(f"Procesando texto: {message_text[:100]}...")
        response = text_model.generate_content(prompt_parts)
        if hasattr(response, '_error') and response._error:
            return f"❌ Error: {response._error}"
        return response.text
    except Exception as e:
        print(f"Error generando respuesta de texto: {e}")
        return "❌ Ocurrió un error al procesar tu mensaje."

async def generate_response_with_image_and_text(image_data, text):
    try:
        image_parts = [{"mime_type": "image/jpeg", "data": image_data}]
        prompt_parts = [image_parts[0], f"\n{text if text else '¿Qué hay en esta imagen?'}"]
        response = image_model.generate_content(prompt_parts)
        if hasattr(response, '_error') and response._error:
            return f"❌ Error: {response._error}"
        return response.text
    except Exception as e:
        print(f"Error procesando imagen: {e}")
        return "❌ No pude procesar la imagen."

#---------------------------------------------Message History-------------------------------------------------
def update_message_history(user_id, text):
    # Check if user_id already exists in the dictionary
    if user_id in message_history:
        # Append the new message to the user's message list
        message_history[user_id].append(text)
        # If there are more than 12 messages, remove the oldest one
        if len(message_history[user_id]) > MAX_HISTORY:
            message_history[user_id].pop(0)
    else:
        # If the user_id does not exist, create a new entry with the message
        message_history[user_id] = [text]

def get_formatted_message_history(user_id):
    """
    Function to return the message history for a given user_id with two line breaks between each message.
    """
    if user_id in message_history:
        # Join the messages with two line breaks
        return '\n\n'.join(message_history[user_id])
    else:
        return "No messages found for this user."

#---------------------------------------------Sending Messages-------------------------------------------------
async def split_and_send_messages(message_system, text, max_length):

    # Split the string into parts
    messages = []
    for i in range(0, len(text), max_length):
        sub_message = text[i:i+max_length]
        messages.append(sub_message)

    # Send each part as a separate message
    for string in messages:
        await message_system.channel.send(string)

def clean_discord_message(input_string):
    # Create a regular expression pattern to match text between < and >
    bracket_pattern = re.compile(r'<[^>]+>')
    # Replace text between brackets with an empty string
    cleaned_content = bracket_pattern.sub('', input_string)
    return cleaned_content




# Cargar extensiones (cogs)
async def load_extensions():
    try:
        await bot.load_extension("moderation")
        await bot.load_extension("entertainment")
        print("✅ Extensiones cargadas correctamente")
    except Exception as e:
        print(f"❌ Error cargando extensiones: {e}")

@bot.event
async def setup_hook():
    await load_extensions()

# Comando de información extendida
@bot.hybrid_command(name="serverinfo", description="Información del servidor")
async def server_info(ctx):
    if not ctx.guild:
        await ctx.send("❌ Este comando solo funciona en servidores.")
        return
    
    guild = ctx.guild
    embed = Embed(title=f"📋 Información de {guild.name}", color=0x7289da)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    
    embed.add_field(name="👑 Propietario", value=guild.owner.mention if guild.owner else "Desconocido", inline=True)
    embed.add_field(name="👥 Miembros", value=guild.member_count, inline=True)
    embed.add_field(name="💬 Canales", value=len(guild.channels), inline=True)
    embed.add_field(name="🎭 Roles", value=len(guild.roles), inline=True)
    embed.add_field(name="📅 Creado", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="🆔 ID", value=guild.id, inline=True)
    
    await ctx.send(embed=embed)

@bot.hybrid_command(name="userinfo", description="Información de un usuario")
async def user_info(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    embed = Embed(title=f"👤 Información de {member.display_name}", color=member.color)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    
    embed.add_field(name="🏷️ Nombre completo", value=str(member), inline=True)
    embed.add_field(name="🆔 ID", value=member.id, inline=True)
    embed.add_field(name="📅 Cuenta creada", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
    
    if ctx.guild and member in ctx.guild.members:
        embed.add_field(name="📥 Se unió al servidor", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="🎭 Roles", value=f"{len(member.roles)-1} roles", inline=True)
        embed.add_field(name="🔝 Rol más alto", value=member.top_role.mention, inline=True)
    
    await ctx.send(embed=embed)

#---------------------------------------------Run Bot-------------------------------------------------
# Solo ejecutar el bot si este archivo es ejecutado directamente
if __name__ == "__main__":
    try:
        bot.run(DISCORD_BOT_TOKEN)
    except Exception as e:
        print(f"Error ejecutando el bot: {e}")