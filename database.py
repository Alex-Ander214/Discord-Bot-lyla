
import os
import pymongo
from datetime import datetime
from typing import Optional, List, Dict

class BotDatabase:
    def __init__(self):
        self.mongodb_uri = os.getenv("MONGODB_URI")
        if not self.mongodb_uri:
            print("⚠️ MONGODB_URI no configurada, usando modo local")
            self.client = None
            self.db = None
            self.conversations = None
            self.users = None
            self.servers = None
            self.stats = None
            return
        
        try:
            self.client = pymongo.MongoClient(self.mongodb_uri)
            # Probar la conexión
            self.client.admin.command('ping')
            self.db = self.client.lyla_bot
            
            # Colecciones
            self.conversations = self.db.conversations
            self.users = self.db.users
            self.servers = self.db.servers
            self.stats = self.db.stats
            
            print("✅ Conexión a MongoDB exitosa")
            # Crear índices para mejor rendimiento
            self.conversations.create_index([("user_id", 1), ("timestamp", -1)])
            self.users.create_index("user_id")
            self.servers.create_index("guild_id")
        except Exception as e:
            print(f"❌ Error conectando a MongoDB: {e}")
            self.client = None
            self.db = None
            self.conversations = None
            self.users = None
            self.servers = None
            self.stats = None
        
    def save_message(self, user_id, message, response, guild_id=None):
        """Guardar conversación en la base de datos"""
        if not self.db:
            return None
            
        conversation = {
            "user_id": str(user_id),
            "guild_id": str(guild_id) if guild_id else None,
            "message": message,
            "response": response,
            "timestamp": datetime.now()
        }
        return self.conversations.insert_one(conversation)
    
    def get_user_history(self, user_id, limit=10):
        """Obtener historial de conversaciones de un usuario"""
        if not self.db:
            return []
            
        query = {"user_id": str(user_id)}
        cursor = self.conversations.find(query).sort("timestamp", -1)
        
        if limit:
            cursor = cursor.limit(limit)
            
        return list(cursor)
    
    def get_formatted_history(self, user_id, limit=10):
        """Obtener historial formateado para el modelo AI"""
        history = self.get_user_history(user_id, limit)
        if not history:
            return ""
            
        formatted = []
        for conv in reversed(history):  # Orden cronológico
            formatted.append(f"Usuario: {conv['message']}")
            formatted.append(f"Asistente: {conv['response']}")
            
        return "\n\n".join(formatted)
    
    def clear_user_history(self, user_id):
        """Limpiar historial de un usuario"""
        if not self.db:
            return type('obj', (object,), {'deleted_count': 0})()
            
        return self.conversations.delete_many({"user_id": str(user_id)})
    
    def update_user_stats(self, user_id, guild_id=None):
        """Actualizar estadísticas de usuario"""
        if not self.db:
            return
            
        self.users.update_one(
            {"user_id": str(user_id)},
            {
                "$inc": {"message_count": 1},
                "$set": {"last_active": datetime.now()},
                "$addToSet": {"guilds": str(guild_id)} if guild_id else {}
            },
            upsert=True
        )
    
    def update_server_stats(self, guild_id):
        """Actualizar estadísticas de servidor"""
        if not self.db:
            return
            
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
        if not self.db:
            return {
                "total_conversations": 0,
                "total_users": 0,
                "total_servers": 0
            }
        
        try:
            total_conversations = self.conversations.count_documents({})
            total_users = self.users.count_documents({})
            total_servers = self.servers.count_documents({})
            
            return {
                "total_conversations": total_conversations,
                "total_users": total_users,
                "total_servers": total_servers
            }
        except Exception as e:
            print(f"Error obteniendo estadísticas globales: {e}")
            return {"total_conversations": 0, "total_users": 0, "total_servers": 0}
    
    def get_user_stats(self, user_id):
        """Obtener estadísticas de usuario específico"""
        if not self.db:
            return {"message_count": 0, "last_active": None}
            
        user = self.users.find_one({"user_id": str(user_id)})
        if user:
            return {
                "message_count": user.get("message_count", 0),
                "last_active": user.get("last_active")
            }
        return {"message_count": 0, "last_active": None}
    
    def get_server_stats(self, guild_id):
        """Obtener estadísticas de servidor específico"""
        if not self.db:
            return {"server_messages": 0, "active_users": 0}
            
        server = self.servers.find_one({"guild_id": str(guild_id)})
        active_users = self.users.count_documents({"guilds": str(guild_id)})
        
        return {
            "server_messages": server.get("message_count", 0) if server else 0,
            "active_users": active_users
        }
