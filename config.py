
import json
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class ServerConfig:
    prefix: str = "!"
    auto_role: Optional[str] = None
    welcome_channel: Optional[str] = None
    log_channel: Optional[str] = None
    level_system: bool = True
    auto_mod: bool = False
    
class ConfigManager:
    def __init__(self):
        self.config_file = 'server_configs.json'
        self.configs = self.load_configs()
    
    def load_configs(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_configs(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.configs, f, indent=4)
    
    def get_config(self, guild_id: str) -> ServerConfig:
        config_data = self.configs.get(guild_id, {})
        return ServerConfig(**config_data)
    
    def update_config(self, guild_id: str, **kwargs):
        if guild_id not in self.configs:
            self.configs[guild_id] = {}
        
        self.configs[guild_id].update(kwargs)
        self.save_configs()
