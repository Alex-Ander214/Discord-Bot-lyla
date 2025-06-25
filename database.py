
import os
import pymongo
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class BotDatabase:
    def __init__(self):
        self.mongodb_uri = os.getenv("MONGODB_URI")
        if not self.mongodb_uri:
            raise ValueError("MONGODB_URI no está configurada en las variables de entorno")
        
        try:
            self.client = pymongo.MongoClient(self.mongodb_uri)
            # Probar la conexión
            self.client.admin.command('ping')
            self.db = self.client.lyla_bot
            print("✅ Conexión a MongoDB exitosa")
        except Exception as e:
            print(f"❌ Error conectando a MongoDB: {e}")
            raise
        
        # Colecciones
        self.conversations = self.db.conversations
        self.users = self.db.users
        self.servers = self.db.servers
        self.stats = self.db.stats
        
    def save_message(self, user_id, message, response, guild_id=None):
        """Guardar conversación en la base de datos"""
        conversation = {
            "user_id": str(user_id),
            "guild_id": str(guild_id) if guild_id else None,
            "message": message,
            "response": response,
            "timestamp": datetime.now()
        }
        return self.conversations.insert_one(conversation)
    
    def get_user_history(self, user_id, limit=None):
        """Obtener historial de conversaciones de un usuario"""
        query = {"user_id": str(user_id)}
        cursor = self.conversations.find(query).sort("timestamp", -1)
        
        if limit:
            cursor = cursor.limit(limit)
            
        return list(cursor)
    
    def get_formatted_history(self, user_id, max_messages):
        """Obtener historial formateado para el modelo de IA"""
        history = self.get_user_history(user_id, max_messages)
        formatted = []
        
        for conv in reversed(history):  # Más reciente al final
            formatted.append(conv["message"])
            formatted.append(conv["response"])
        
        return '\n\n'.join(formatted)
    
    def clear_user_history(self, user_id):
        """Limpiar historial de un usuario"""
        return self.conversations.delete_many({"user_id": str(user_id)})
    
    def update_user_stats(self, user_id, guild_id=None):
        """Actualizar estadísticas de usuario"""
        user_data = {
            "user_id": str(user_id),
            "last_active": datetime.now(),
            "message_count": 1
        }
        
        if guild_id:
            user_data["guild_id"] = str(guild_id)
        
        self.users.update_one(
            {"user_id": str(user_id)},
            {"$inc": {"message_count": 1}, "$set": {"last_active": datetime.now()}},
            upsert=True
        )
    
    def update_server_stats(self, guild_id):
        """Actualizar estadísticas de servidor"""
        self.servers.update_one(
            {"guild_id": str(guild_id)},
            {
                "$inc": {"message_count": 1},
                "$set": {"last_active": datetime.now()}
            },
            upsert=True
        )
    
    def get_global_stats(self):
        """Obtener estadísticas globales"""
        total_conversations = self.conversations.count_documents({})
        total_users = self.users.count_documents({})
        total_servers = self.servers.count_documents({})
        
        return {
            "total_conversations": total_conversations,
            "total_users": total_users,
            "total_servers": total_servers
        }
    
    def get_server_stats(self, guild_id):
        """Obtener estadísticas de un servidor específico"""
        server_messages = self.conversations.count_documents({"guild_id": str(guild_id)})
        server_users = self.conversations.distinct("user_id", {"guild_id": str(guild_id)})
        
        return {
            "server_messages": server_messages,
            "active_users": len(server_users)
        }
    
    def get_user_stats(self, user_id):
        """Obtener estadísticas de un usuario específico"""
        user_data = self.users.find_one({"user_id": str(user_id)})
        if not user_data:
            return {"message_count": 0, "last_active": None}
        
        return {
            "message_count": user_data.get("message_count", 0),
            "last_active": user_data.get("last_active")
        }
