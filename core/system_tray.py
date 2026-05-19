import threading
import tkinter as tk
from tkinter import messagebox
import logging
import time
import sys

try:
    import pystray  # type: ignore
    from PIL import Image, ImageDraw  # type: ignore
except ImportError:
    pystray = None
    Image = None
    ImageDraw = None

from logic.resources import get_resource_usage

class SystemTray:
    def __init__(self, app=None):
        self.app = app
        self.icon = None
        self.tray_thread = None
        self.logger = logging.getLogger("android_studio")
        self.current_status = "stopped"  # stopped, running, paused
        self.tray_enabled = True
        if app and hasattr(app, 'config'):
            self.tray_enabled = app.config.get('ui', {}).get('tray_enabled', True)
        
        if self.tray_enabled:
            self.setup_system_tray()

    def create_status_icon(self, status):
        """Create a premium, modern icon based on status"""
        if not Image or not ImageDraw:
            return None
            
        # Define high-end color palette (HSL-based for vibrancy)
        status_colors = {
            "running": {"primary": (46, 204, 113), "glow": (39, 174, 96)},   # Emerald Green
            "paused": {"primary": (52, 152, 219), "glow": (41, 128, 185)},    # Peter River Blue
            "stopped": {"primary": (231, 76, 60), "glow": (192, 57, 43)},    # Alizarin Red
        }
        
        config = status_colors.get(status, {"primary": (149, 165, 166), "glow": (127, 140, 141)})
        primary = config["primary"]
        glow = config["glow"]
        
        # Create a 64x64 canvas for higher quality drawing (then scale down)
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw a soft outer glow/shadow
        margin = 4
        draw.ellipse([margin, margin, size-margin, size-margin], fill=glow + (50,))
        
        # Draw the main status orb with a subtle gradient effect
        margin = 10
        draw.ellipse([margin, margin, size-margin, size-margin], fill=primary + (255,))
        
        # Add a "Glass" highlight (top-left)
        highlight_margin = 14
        draw.ellipse([highlight_margin, highlight_margin, size//2 + 5, size//2 + 5], 
                    fill=(255, 255, 255, 100))
        
        # Add a subtle border
        draw.ellipse([margin, margin, size-margin, size-margin], 
                    outline=(255, 255, 255, 180), width=3)

        # Scale down to 16x16 (Windows default tray size) for crispness
        return image.resize((16, 16), Image.Resampling.LANCZOS)

    def update_status(self, status):
        """Update the tray icon status and color"""
        if not self.icon or not pystray:
            return
            
        self.current_status = status
        status_text = {
            "stopped": "AndroidStudioV1 - Stopped",
            "running": "AndroidStudioV1 - Active", 
            "paused": "AndroidStudioV1 - Paused"
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
                    pystray.MenuItem(lambda item: "Resume" if self.current_status == "paused" else "Pause", self._tray_toggle_pause),
                    pystray.MenuItem("Start", self._tray_start_simulation),
                    pystray.MenuItem("Stop", self._tray_stop_simulation),
                    pystray.MenuItem("Exit", self._tray_exit_application)
                )
                self.icon = pystray.Icon("AndroidStudio", image, "AndroidStudioV1 - Stopped", menu)
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
        
        # Reschedule update safely to prevent exceptions during app shutdown
        try:
            if hasattr(self, 'app') and self.app and hasattr(self.app, 'root') and self.app.root:
                self.app.root.after(2000, self._schedule_resource_tooltip_update)
            else:
                # For CLI mode, use a timer
                import threading
                timer = threading.Timer(2.0, self._schedule_resource_tooltip_update)
                timer.daemon = True
                timer.start()
        except Exception:
            pass

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
        if self.app and hasattr(self.app, 'root'):
            self.app.root.after(0, self.app.show_window)
        else:
            self.logger.info("Show Window: Not available in CLI mode.")

    def _tray_toggle_pause(self, icon=None, item=None):
        if self.app:
            self.app.toggle_pause()

    def _tray_start_simulation(self, icon=None, item=None):
        if self.app and hasattr(self.app, 'root'):
            self.app.root.after(0, self.app.start_simulation)
        elif self.app:
            self.app.start_simulation()

    def _tray_stop_simulation(self, icon=None, item=None):
        if self.app and hasattr(self.app, 'root'):
            self.app.root.after(0, self.app.stop_simulation)
        elif self.app:
            self.app.stop_simulation()

    def _tray_exit_application(self, icon=None, item=None):
        if self.app and hasattr(self.app, 'root'):
            self.app.root.after(0, self.app.exit_application)
        else:
            import os
            self.logger.info("Exiting application...")
            os._exit(0)

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
