import json
import os
from tkinter import messagebox

class ConfigManager:
    def __init__(self, config_file=None):
        # Use per-user config in %APPDATA%/AndroidStudioV1/anoid.json by default
        if config_file is None:
            appdata = os.environ.get('APPDATA')
            if appdata:
                config_dir = os.path.join(appdata, 'AndroidStudioV1')
                os.makedirs(config_dir, exist_ok=True)
                config_file = os.path.join(config_dir, 'anoid.json')
            else:
                # Fallback to local config directory if APPDATA is not set
                config_dir = os.path.join(os.getcwd(), 'config')
                os.makedirs(config_dir, exist_ok=True)
                config_file = os.path.join(config_dir, 'anoid.json')
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as file:
                return json.load(file)
        except Exception as e:
            if self._notifications_enabled():
                messagebox.showerror("Error", f"Failed to load configuration: {e}")
            return {}

    def save_config(self, config=None):
        try:
            if config is None:
                config = self.config
            with open(self.config_file, 'w') as file:
                json.dump(config, file, indent=2)
            if self._notifications_enabled():
                messagebox.showinfo("Success", "Configuration saved successfully.")
        except Exception as e:
            if self._notifications_enabled():
                messagebox.showerror("Error", f"Failed to save configuration: {e}")

    def update_config(self, new_config):
        self.config = new_config
        self.save_config()

    def reset_to_defaults(self):
        import shutil
        import os
        default_config_path = os.path.join(os.path.dirname(__file__), 'config', 'default_anoid.json')
        if not os.path.exists(default_config_path):
            # Try relative to project root
            default_config_path = os.path.join(os.getcwd(), 'config', 'default_anoid.json')
        if os.path.exists(default_config_path):
            try:
                shutil.copyfile(default_config_path, self.config_file)
                self.config = self.load_config()
                return True, None
            except Exception as e:
                return False, str(e)
        else:
            return False, 'Default config not found.'

    def _notifications_enabled(self):
        try:
            with open(self.config_file, 'r') as file:
                config = json.load(file)
                return config.get('ui', {}).get('notifications_enabled', False)
        except Exception:
            return True  # Fail open: show notifications if config can't be read
