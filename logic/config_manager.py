import json
import os
import logging

class ConfigManager:
    def __init__(self, config_file=None):
        self.logger = logging.getLogger("android_studio")
        # Use local config/anoid.json for consistency in this project
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_dir = os.path.join(project_root, 'config')
        os.makedirs(config_dir, exist_ok=True)
        
        if config_file is None:
            config_file = os.path.join(config_dir, 'anoid.json')
            
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as file:
                    return json.load(file)
            return self.get_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return self.get_default_config()

    def get_config(self):
        """Always reload config to get latest changes"""
        self.config = self.load_config()
        return self.config

    def save_config(self, config=None):
        try:
            if config is None:
                config = self.config
            with open(self.config_file, 'w') as file:
                json.dump(config, file, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")

    def update_config(self, new_config):
        self.config = new_config
        self.save_config()

    def get_default_config(self):
        """Return a basic default config if none exists"""
        return {
            'mouse': {'enabled': True, 'movements': 3, 'min_duration': 0.5, 'max_duration': 2.0, 'min_interval': 1.0, 'max_interval': 5.0},
            'keyboard': {'enabled': True, 'actions': 2, 'phrases': ['coding...', 'android studio'], 'min_interval': 2.0, 'max_interval': 10.0},
            'ui': {'tray_enabled': True, 'auto_start_simulation': True, 'notifications_enabled': False}
        }
