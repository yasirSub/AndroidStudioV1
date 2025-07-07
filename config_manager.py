import json
import os
from tkinter import messagebox

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as file:
                return json.load(file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {e}")
            return {}

    def save_config(self, config=None):
        try:
            if config is None:
                config = self.config
            with open(self.config_file, 'w') as file:
                json.dump(config, file, indent=2)
            messagebox.showinfo("Success", "Configuration saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")

    def update_config(self, new_config):
        self.config = new_config
        self.save_config()
