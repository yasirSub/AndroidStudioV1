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

from logic.resources import get_resource_usage

class SystemTray:
    def __init__(self, app):
        self.app = app
        self.icon = None
        self.tray_thread = None
        self.logger = logging.getLogger("android_studio")
        self.current_status = "stopped"  # stopped, running, paused
        self.tray_enabled = getattr(app, 'tray_enabled', True)  # Default to True
        if self.tray_enabled:
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
        
        # Create a 16x16 image with the status color (standard Windows tray icon size)
        image = Image.new('RGBA', (16, 16), color + (0,))
        draw = ImageDraw.Draw(image)
        # Add a simple status indicator (circle in center)
        center_x, center_y = 8, 8
        radius = 5
        # Draw outer circle
        draw.ellipse([center_x - radius, center_y - radius, 
                     center_x + radius, center_y + radius], 
                    outline=(255, 255, 255, 255), width=2)
        # Draw inner circle based on status
        if status == "running":
            draw.ellipse([center_x - radius + 1, center_y - radius + 1,
                         center_x + radius - 1, center_y + radius - 1],
                        fill=(0, 200, 0, 255))
        elif status == "paused":
            draw.ellipse([center_x - radius + 1, center_y - radius + 1,
                         center_x + radius - 1, center_y + radius - 1],
                        fill=(0, 0, 200, 255))
        elif status == "stopped":
            draw.ellipse([center_x - radius + 1, center_y - radius + 1,
                         center_x + radius - 1, center_y + radius - 1],
                        fill=(200, 0, 0, 255))
        return image

    def update_status(self, status):
        """Update the tray icon status and color"""
        if not self.icon or not pystray:
            return
            
        self.current_status = status
        status_text = {
            "stopped": "Android Studio - Stopped",
            "running": "Android Studio - Active", 
            "paused": "Android Studio - Paused"
        }
        
        try:
            # Create new icon with updated status
            new_image = self.create_status_icon(status)
            if new_image:
                self.icon.icon = new_image
                self.icon.title = status_text.get(status, "Android Studio")
        except Exception as e:
            self.logger.error(f"Failed to update tray status: {e}")

    def update_tray_resource_tooltip(self):
        usage = get_resource_usage()
        tooltip = f"CPU: {usage['cpu_percent']:.1f}%\nRAM: {usage['ram_mb']:.1f} MB"
        if usage['gpu_percent'] is not None:
            tooltip += f"\nGPU: {usage['gpu_percent']:.1f}%"
        if hasattr(self, 'icon') and self.icon:
            self.icon.title = tooltip

    def setup_system_tray(self):
        if not self.tray_enabled:
            return
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
                self.icon = pystray.Icon("AndroidStudio", image, "Android Studio - Stopped", menu)
                self.tray_thread = threading.Thread(target=self.icon.run, daemon=True)
                self.tray_thread.start()
                self._schedule_resource_tooltip_update()
            except Exception as e:
                self.icon = None
                self.logger.warning(f"Failed to initialize system tray: {e}")
        else:
            self.icon = None
            self.logger.warning("pystray or PIL not installed. System tray icon will be disabled.")

    def _schedule_resource_tooltip_update(self):
        try:
            self.update_tray_resource_tooltip()
        except Exception:
            pass
        if hasattr(self, 'app') and hasattr(self.app, 'root'):
            self.app.root.after(2000, self._schedule_resource_tooltip_update)

    def minimize_to_tray(self):
        if self.icon:
            try:
                self.app.root.after(200, self.app.root.withdraw)
            except Exception as e:
                self.logger.error(f"Failed to minimize to tray: {e}")
                if self.app.config.get('ui', {}).get('notifications_enabled', False):
                    from tkinter import messagebox
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

    def hide_tray_icon(self):
        if self.icon:
            try:
                self.icon.stop()
                self.icon = None
            except Exception as e:
                self.logger.warning(f"Failed to hide tray icon: {e}")
