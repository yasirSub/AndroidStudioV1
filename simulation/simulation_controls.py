import threading
import time
import random
import sys
import logging
from core.engine import SimulationEngine

class SimulationControls:
    def __init__(self, app):
        self.app = app
        self.engine = SimulationEngine(app.config_manager if hasattr(app, 'config_manager') else app, app.logger)
        self.engine.set_status_callback(self._on_status_change)
        self.simulation_running = False
        self.user_activity_listener = None
        self.logger = logging.getLogger("android_studio")

    def _on_status_change(self, status):
        self.simulation_running = (status == "running")
        if hasattr(self.app, 'system_tray'):
            self.app.system_tray.update_status(status)
        if hasattr(self.app, 'ui_components') and hasattr(self.app.ui_components, 'status_label'):
            status_text = f"Status: {status.capitalize()}"
            self.app.ui_components.status_label.config(text=status_text)

    def start_simulation(self):
        if not self.simulation_running:
            self.engine.start()
            if hasattr(self.app, 'system_tray'):
                self.app.root.after(200, self.app.system_tray.minimize_to_tray)
        else:
            self.app.notify_warning("Warning", "Simulation is already running.")

    def stop_simulation(self):
        if self.simulation_running:
            self.engine.stop()
        else:
            self.app.notify_warning("Warning", "No simulation is running.")


    def toggle_simulation_hotkey(self):
        if self.simulation_running:
            self.stop_simulation()
        else:
            self.start_simulation()
