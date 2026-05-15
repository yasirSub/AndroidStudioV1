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
            self.start_user_activity_listener()
        else:
            self.app.notify_warning("Warning", "Simulation is already running.")

    def stop_simulation(self):
        if self.simulation_running:
            self.engine.stop()
            self.stop_user_activity_listener()
        else:
            self.app.notify_warning("Warning", "No simulation is running.")

    def start_user_activity_listener(self):
        try:
            from pynput import mouse, keyboard
            self.stop_user_activity_listener()
            self.resume_timer = None
            
            def on_activity(*args, **kwargs):
                # Pause if not already paused
                if self.simulation_running and not self.engine.paused:
                    self.engine.toggle_pause()
                
                # Reset the resume timer on every activity
                if hasattr(self, 'resume_timer') and self.resume_timer:
                    self.resume_timer.cancel()
                
                # Schedule resume after 10 seconds of NO activity
                self.resume_timer = threading.Timer(10.0, self._check_resume)
                self.resume_timer.start()
            
            self.user_activity_listener = {
                'mouse': mouse.Listener(on_move=on_activity, on_click=on_activity, on_scroll=on_activity),
                'keyboard': keyboard.Listener(on_press=on_activity)
            }
            self.user_activity_listener['mouse'].start()
            self.user_activity_listener['keyboard'].start()
        except ImportError:
            self.logger.warning("pynput not installed. User activity detection disabled.")

    def _check_resume(self):
        """Automatically resume simulation if user is still idle"""
        if self.simulation_running and self.engine.paused:
            self.logger.info("Inactivity detected for 10s. Resuming simulation...")
            self.engine.toggle_pause()
            self.resume_timer = None

    def stop_user_activity_listener(self):
        if self.user_activity_listener:
            for l in self.user_activity_listener.values():
                try: l.stop()
                except: pass
            self.user_activity_listener = None

    def toggle_simulation_hotkey(self):
        if self.simulation_running:
            self.stop_simulation()
        else:
            self.start_simulation()
