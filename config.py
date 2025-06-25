
import json
import os
from dataclasses import dataclass, asdict

@dataclass
class ServerConfig:
    """Configuración por servidor"""
    prefix: str = "/"
    moderation_enabled: bool = True
    logging_enabled: bool = True
    welcome_channel: str = None
    mod_channel: str = None
    auto_role: str = None
    banned_words: list = None
    
    def __post_init__(self):
        if self.banned_words is None:
            self.banned_words = []

class ConfigManager:
    def __init__(self):
        self.config_file = "server_configs.json"
        self.configs = self._load_configs()

    def _load_configs(self):
        """Cargar configuraciones desde archivo"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {k: ServerConfig(**v) for k, v in data.items()}
            except Exception as e:
                print(f"Error cargando configuraciones: {e}")
        return {}

    def _save_configs(self):
        """Guardar configuraciones al archivo"""
        try:
            data = {k: asdict(v) for k, v in self.configs.items()}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando configuraciones: {e}")

    def get_config(self, guild_id: str) -> ServerConfig:
        """Obtener configuración de un servidor"""
        if guild_id not in self.configs:
            self.configs[guild_id] = ServerConfig()
            self._save_configs()
        return self.configs[guild_id]

    def update_config(self, guild_id: str, **kwargs):
        """Actualizar configuración de un servidor"""
        config = self.get_config(guild_id)
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        self._save_configs()
        return config
