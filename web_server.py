
from flask import Flask, jsonify, render_template_string
import threading
import os
import logging
import time
from main import bot, DISCORD_BOT_TOKEN, db

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

@app.route('/dashboard')
def dashboard():
    """Dashboard web con estadísticas"""
    if not db:
        return jsonify({"error": "Database not available"}), 503
    
    try:
        global_stats = db.get_global_stats()
        
        dashboard_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Lyla Bot Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #2c2f33; color: white; }
                .container { max-width: 1200px; margin: 0 auto; }
                .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
                .stat-card { background: #36393f; padding: 20px; border-radius: 10px; border-left: 4px solid #7289da; }
                .stat-number { font-size: 2em; font-weight: bold; color: #7289da; }
                h1 { color: #7289da; text-align: center; }
                h2 { color: #99aab5; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Lyla Bot Dashboard</h1>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h2>💬 Total Conversaciones</h2>
                        <div class="stat-number">{{ total_conversations }}</div>
                    </div>
                    <div class="stat-card">
                        <h2>👥 Usuarios Únicos</h2>
                        <div class="stat-number">{{ total_users }}</div>
                    </div>
                    <div class="stat-card">
                        <h2>🏠 Servidores</h2>
                        <div class="stat-number">{{ total_servers }}</div>
                    </div>
                    <div class="stat-card">
                        <h2>🟢 Estado del Bot</h2>
                        <div class="stat-number">{{ bot_status }}</div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return render_template_string(dashboard_html, 
                                    total_conversations=global_stats['total_conversations'],
                                    total_users=global_stats['total_users'],
                                    total_servers=global_stats['total_servers'],
                                    bot_status="🟢 Online" if bot.is_ready() else "🟡 Connecting")
    except Exception as e:
        logger.error(f"Error in dashboard: {e}")
        return jsonify({"error": "Failed to load dashboard"}), 500

@app.route('/api/conversations/<user_id>')
def get_user_conversations(user_id):
    """API para obtener conversaciones de un usuario"""
    if not db:
        return jsonify({"error": "Database not available"}), 503
    
    try:
        conversations = db.get_user_history(user_id, 50)  # Últimas 50
        return jsonify({
            "user_id": user_id,
            "conversation_count": len(conversations),
            "conversations": [
                {
                    "message": conv["message"],
                    "response": conv["response"][:100] + "..." if len(conv["response"]) > 100 else conv["response"],
                    "timestamp": conv["timestamp"].isoformat()
                } for conv in conversations
            ]
        })
    except Exception as e:
        logger.error(f"Error getting user conversations: {e}")
        return jsonify({"error": "Failed to get conversations"}), 500

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
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

if __name__ == '__main__':
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Give the bot a moment to start
    time.sleep(2)
    
    # Start web server in main thread
    run_web_server()
