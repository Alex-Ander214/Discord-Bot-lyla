
from flask import Flask, jsonify
import threading
import os
from main import bot, DISCORD_BOT_TOKEN

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "Bot is running",
        "bot_name": bot.user.name if bot.user else "Bot not ready",
        "guild_count": len(bot.guilds) if bot.is_ready() else 0
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "bot_ready": bot.is_ready()
    })

@app.route('/stats')
def stats():
    if not bot.is_ready():
        return jsonify({"error": "Bot not ready"}), 503
    
    return jsonify({
        "guild_count": len(bot.guilds),
        "user_count": sum(guild.member_count for guild in bot.guilds),
        "bot_name": bot.user.name,
        "bot_id": bot.user.id
    })

def run_bot():
    """Run the Discord bot in a separate thread"""
    bot.run(DISCORD_BOT_TOKEN)

def run_web_server():
    """Run the Flask web server"""
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Start web server in main thread
    run_web_server()
