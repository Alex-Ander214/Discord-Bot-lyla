
from flask import Flask, jsonify
import threading
import os
import logging
import time
from main import bot, DISCORD_BOT_TOKEN

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    try:
        bot_status = "ready" if bot.is_ready() else "connecting"
        return jsonify({
            "status": "Bot is running",
            "bot_status": bot_status,
            "bot_name": bot.user.name if bot.user else "Lyla",
            "guild_count": len(bot.guilds) if bot.is_ready() else 0,
            "version": "1.0.0",
            "message": "Lyla Discord Bot está funcionando correctamente"
        })
    except Exception as e:
        logger.error(f"Error in home route: {e}")
        return jsonify({
            "status": "Bot is running", 
            "message": "Lyla Discord Bot está funcionando",
            "version": "1.0.0"
        })

@app.route('/health')
def health():
    try:
        return jsonify({
            "status": "healthy",
            "bot_ready": bot.is_ready(),
            "uptime": "online",
            "timestamp": int(time.time())
        })
    except Exception as e:
        logger.error(f"Error in health route: {e}")
        return jsonify({"status": "healthy", "message": "Service is running"}), 200

@app.route('/stats')
def stats():
    try:
        if not bot.is_ready():
            return jsonify({
                "message": "Bot is connecting...",
                "guild_count": 0,
                "user_count": 0,
                "bot_name": "Lyla"
            })
        
        return jsonify({
            "guild_count": len(bot.guilds),
            "user_count": sum(guild.member_count for guild in bot.guilds if guild.member_count),
            "bot_name": bot.user.name,
            "bot_id": bot.user.id,
            "latency": round(bot.latency * 1000, 2)
        })
    except Exception as e:
        logger.error(f"Error in stats route: {e}")
        return jsonify({"error": "Failed to get stats"}), 500

def run_bot():
    """Run the Discord bot in a separate thread"""
    try:
        logger.info("Starting Discord bot...")
        bot.run(DISCORD_BOT_TOKEN)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

def run_web_server():
    """Run the Flask web server"""
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting web server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Give the bot a moment to start
    time.sleep(2)
    
    # Start web server in main thread
    run_web_server()
