import threading
import tkinter as tk
from tkinter import messagebox
import logging

try:
    import pystray  # type: ignore
    from PIL import Image  # type: ignore
except ImportError:
    pystray = None
    Image = None

class SystemTray:
    def __init__(self, app):
        self.app = app
        self.icon = None
        self.tray_thread = None
        self.logger = logging.getLogger("anoid")
        self.setup_system_tray()

    def setup_system_tray(self):
        if pystray and Image:
            try:
                image = Image.new('RGB', (64, 64), color='blue')
                menu = (
                    pystray.MenuItem("Show", self._tray_show_window),
                    pystray.MenuItem("Start", self._tray_start_simulation),
                    pystray.MenuItem("Stop", self._tray_stop_simulation),
                    pystray.MenuItem("Exit", self._tray_exit_application)
                )
                self.icon = pystray.Icon("Anoid", image, "Anoid", menu)
                self.tray_thread = threading.Thread(target=self.icon.run, daemon=True)
                self.tray_thread.start()
            except Exception as e:
                self.icon = None
                self.logger.warning(f"Failed to initialize system tray: {e}")
        else:
            self.icon = None
            self.logger.warning("pystray or PIL not installed. System tray icon will be disabled.")

    def minimize_to_tray(self):
        if self.icon:
            try:
                self.app.root.after(200, self.app.root.withdraw)
            except Exception as e:
                self.logger.error(f"Failed to minimize to tray: {e}")
                messagebox.showerror("Error", f"Failed to minimize to tray: {e}")
                self.app.show_window()

    def _tray_show_window(self, icon=None, item=None):
        self.app.root.after(0, self.app.show_window)

    def _tray_start_simulation(self, icon=None, item=None):
        self.app.root.after(0, self.app.start_simulation)

    def _tray_stop_simulation(self, icon=None, item=None):
        self.app.root.after(0, self.app.stop_simulation)

    def _tray_exit_application(self, icon=None, item=None):
        self.app.root.after(0, self.app.exit_application)

    def stop(self):
        try:
            if self.icon:
                self.icon.stop()
        except Exception:
            pass
