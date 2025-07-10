import threading
import tkinter as tk
from tkinter import messagebox
import logging

try:
    import pystray  # type: ignore
    from PIL import Image, ImageDraw  # type: ignore
except ImportError:
    pystray = None
    Image = None
    ImageDraw = None

class SystemTray:
    def __init__(self, app):
        self.app = app
        self.icon = None
        self.tray_thread = None
        self.logger = logging.getLogger("anoid")
        self.current_status = "stopped"  # stopped, running, paused
        self.setup_system_tray()

    def create_status_icon(self, status):
        """Create a colored icon based on status"""
        if not Image or not ImageDraw:
            return None
            
        # Color mapping
        colors = {
            "stopped": (255, 0, 0),    # Red
            "running": (0, 255, 0),    # Green  
            "paused": (0, 0, 255)      # Blue
        }
        
        color = colors.get(status, (128, 128, 128))  # Gray as default
        
        # Create a 64x64 image with the status color
        image = Image.new('RGB', (64, 64), color)
        draw = ImageDraw.Draw(image)
        
        # Add a simple status indicator (circle in center)
        center_x, center_y = 32, 32
        radius = 20
        
        # Draw outer circle
        draw.ellipse([center_x - radius, center_y - radius, 
                     center_x + radius, center_y + radius], 
                    outline=(255, 255, 255), width=2)
        
        # Draw inner circle based on status
        if status == "running":
            # Green circle for running
            draw.ellipse([center_x - radius + 4, center_y - radius + 4,
                         center_x + radius - 4, center_y + radius - 4],
                        fill=(0, 200, 0))
        elif status == "paused":
            # Blue circle for paused
            draw.ellipse([center_x - radius + 4, center_y - radius + 4,
                         center_x + radius - 4, center_y + radius - 4],
                        fill=(0, 0, 200))
        elif status == "stopped":
            # Red circle for stopped
            draw.ellipse([center_x - radius + 4, center_y - radius + 4,
                         center_x + radius - 4, center_y + radius - 4],
                        fill=(200, 0, 0))
        
        return image

    def update_status(self, status):
        """Update the tray icon status and color"""
        if not self.icon or not pystray:
            return
            
        self.current_status = status
        status_text = {
            "stopped": "Anoid - Stopped",
            "running": "Anoid - Running", 
            "paused": "Anoid - Paused"
        }
        
        try:
            # Create new icon with updated status
            new_image = self.create_status_icon(status)
            if new_image:
                self.icon.icon = new_image
                self.icon.title = status_text.get(status, "Anoid")
        except Exception as e:
            self.logger.error(f"Failed to update tray status: {e}")

    def setup_system_tray(self):
        if pystray and Image:
            try:
                # Create initial icon (stopped status)
                image = self.create_status_icon("stopped")
                menu = (
                    pystray.MenuItem("Show", self._tray_show_window),
                    pystray.MenuItem("Start", self._tray_start_simulation),
                    pystray.MenuItem("Stop", self._tray_stop_simulation),
                    pystray.MenuItem("Exit", self._tray_exit_application)
                )
                self.icon = pystray.Icon("Anoid", image, "Anoid - Stopped", menu)
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
