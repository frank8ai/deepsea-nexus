"""
Simple configuration module for testing
"""
import os
import json


class SimpleConfig:
    """Simple configuration loader"""
    
    def __init__(self):
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        config_file = os.path.join(os.getcwd(), "config.json")
        print("Looking for config at:", config_file)  # Debug
        print("File exists:", os.path.exists(config_file))  # Debug
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.config = json.load(f)
                print("Config loaded successfully:", self.config.get('project', {}).get('name'))  # Debug
        else:
            print("Config file not found, using defaults")
            self.config = self.default_config()
    
    def default_config(self):
        """Return default config"""
        return {
            "project": {
                "name": "Deep-Sea Nexus v2.0",
                "version": "2.0.0"
            }
        }
    
    def get(self, key, default=None):
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        return value if value is not None else default


# Test the simple config
simple_config = SimpleConfig()
print("Testing simple config:", simple_config.get('project.name'))
