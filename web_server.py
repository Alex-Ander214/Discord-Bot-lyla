
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
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0d1117; color: #c9d1d9; line-height: 1.6; }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                .header { text-align: center; margin-bottom: 40px; }
                .header h1 { color: #58a6ff; font-size: 2.5em; margin-bottom: 10px; }
                .header p { color: #8b949e; font-size: 1.2em; }
                .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 25px; margin-bottom: 40px; }
                .stat-card { background: linear-gradient(145deg, #161b22, #21262d); padding: 25px; border-radius: 12px; border: 1px solid #30363d; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.2s; }
                .stat-card:hover { transform: translateY(-2px); }
                .stat-icon { font-size: 2.5em; margin-bottom: 15px; }
                .stat-number { font-size: 2.2em; font-weight: bold; color: #58a6ff; margin-bottom: 5px; }
                .stat-label { color: #8b949e; font-size: 1.1em; font-weight: 500; }
                .server-list { background: #161b22; padding: 25px; border-radius: 12px; border: 1px solid #30363d; margin-top: 20px; }
                .server-item { background: #21262d; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #58a6ff; }
                .server-name { font-weight: bold; color: #f0f6fc; margin-bottom: 5px; }
                .server-stats { color: #8b949e; font-size: 0.9em; }
                .refresh-btn { background: #238636; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; margin-top: 20px; }
                .refresh-btn:hover { background: #2ea043; }
                .status-online { color: #3fb950; }
                .status-offline { color: #f85149; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 Lyla Bot Dashboard</h1>
                    <p>Panel de control y estadísticas en tiempo real</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon">💬</div>
                        <div class="stat-number">{{ total_conversations }}</div>
                        <div class="stat-label">Total Conversaciones</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">👥</div>
                        <div class="stat-number">{{ total_users }}</div>
                        <div class="stat-label">Usuarios Únicos</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">🏠</div>
                        <div class="stat-number">{{ total_servers }}</div>
                        <div class="stat-label">Servidores Conectados</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">🟢</div>
                        <div class="stat-number status-{{ 'online' if bot_online else 'offline' }}">{{ bot_status }}</div>
                        <div class="stat-label">Estado del Bot</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">⚡</div>
                        <div class="stat-number">{{ latency }}ms</div>
                        <div class="stat-label">Latencia</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">📊</div>
                        <div class="stat-number">{{ uptime }}</div>
                        <div class="stat-label">Tiempo Activo</div>
                    </div>
                </div>
                
                <div class="server-list">
                    <h2 style="color: #f0f6fc; margin-bottom: 20px;">🌐 Servidores Activos</h2>
                    {% for server in servers %}
                    <div class="server-item">
                        <div class="server-name">{{ server.name }}</div>
                        <div class="server-stats">👥 {{ server.members }} miembros • 💬 {{ server.channels }} canales</div>
                    </div>
                    {% endfor %}
                </div>
                
                <button class="refresh-btn" onclick="location.reload()">🔄 Actualizar Datos</button>
            </div>
            
            <script>
                // Auto-refresh cada 30 segundos
                setTimeout(() => location.reload(), 30000);
            </script>
        </body>
        </html>
        """
        
        # Información adicional del bot
        bot_info = {
            "bot_online": bot.is_ready(),
            "latency": round(bot.latency * 1000, 2) if bot.is_ready() else 0,
            "uptime": "24/7",
            "servers": [
                {
                    "name": guild.name,
                    "members": guild.member_count,
                    "channels": len(guild.channels)
                } for guild in bot.guilds[:10]  # Primeros 10 servidores
            ] if bot.is_ready() else []
        }
        
        return render_template_string(dashboard_html, 
                                    total_conversations=global_stats['total_conversations'],
                                    total_users=global_stats['total_users'],
                                    total_servers=global_stats['total_servers'],
                                    bot_status="Online" if bot.is_ready() else "Connecting",
                                    **bot_info)
    except Exception as e:
        logger.error(f"Error in dashboard: {e}")
        return jsonify({"error": "Dashboard error", "details": str(e)}), 500

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
