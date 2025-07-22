# pyright: reportOptionalMemberAccess=false
import tkinter as tk
import json
import logging
import sys
import os
import shutil
from tkinter import messagebox
import keyboard as global_keyboard  # for hotkey  # type: ignore

# Add the project root directory to sys.path to ensure imports work correctly
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.system_tray import SystemTray
from ui.ui_components import UIComponents
from simulation.simulation_controls import SimulationControls

class AndroidStudioUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Android Studio")
        self.root.geometry("900x700")  # Larger window for modern UI
        self.root.minsize(800, 600)
        
        # Set modern window properties
        self.root.configure(bg='#F7FAFC')  # Light background as default
        
        # Center the window on screen
        self.center_window()
        
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.config_file = os.path.join(project_root, "config", "anoid.json")
        self.log_file = os.path.join(project_root, "config", "anoid.log")
        
        # Migrate old config/log if found
        self.migrate_old_files()
        self.config = self.load_config()
        self.process = None
        self.log_messages = []
        self.auto_restart_enabled = self.config.get('ui', {}).get('auto_restart', True)
        self.auto_restart_timer = None
        self.idle_timeout_minutes = self.config.get('ui', {}).get('idle_timeout_minutes', 1)
        self.user_is_idle = False
        
        self.setup_logging()
        
        # Initialize components
        self.system_tray = SystemTray(self)
        self.ui_components = UIComponents(self)
        self.simulation_controls = SimulationControls(self)
        
        # Setup UI after components are initialized
        self.setup_ui()
        
        # Window management
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Apply theme
        self.ui_components.apply_theme()
        
        # Global hotkey for pause/resume
        try:
            global_keyboard.add_hotkey('ctrl+shift+p', self.simulation_controls.toggle_simulation_hotkey)
        except Exception:
            pass
        
        # Set window icon if available
        self.set_window_icon()
        
        # Check for first run to open GitHub link
        self.check_and_open_github_on_first_run()

    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def set_window_icon(self):
        """Set the window icon if available"""
        try:
            # Try ICO file first
            icon_path = os.path.join(project_root, "Android_Studio_icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
            else:
                # Fallback to SVG (not supported by Tkinter, so just pass)
                pass
        except Exception:
            # Silently fail if icon setting fails
            pass

    def migrate_old_files(self):
        """Migrate old configuration and log files to new locations"""
        # Migrate config.json to anoid.json if present
        if os.path.exists("config.json") and not os.path.exists(self.config_file):
            try:
                shutil.move("config.json", self.config_file)
            except Exception:
                pass
        
        # Migrate android_studio.log to anoid.log if present
        if os.path.exists("android_studio.log") and not os.path.exists(self.log_file):
            try:
                shutil.move("android_studio.log", self.log_file)
            except Exception:
                pass

    def setup_logging(self):
        """Setup logging configuration"""
        try:
            # Ensure log directory exists
            log_dir = os.path.dirname(self.log_file)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Only log to file, not to console
            logging.basicConfig(
                level=logging.INFO, 
                format='%(asctime)s - %(levelname)s - %(message)s', 
                handlers=[logging.FileHandler(self.log_file)]
            )
        except Exception as e:
            messagebox.showerror("Error", f"Cannot create log file: {e}")
            self.root.destroy()
            sys.exit(1)
        
        self.logger = logging.getLogger("android_studio")
        self.log_handler = self.LogHandler(self)
        self.logger.addHandler(self.log_handler)

    class LogHandler(logging.Handler):
        """Custom log handler for UI updates"""
        def __init__(self, ui):
            super().__init__()
            self.ui = ui

        def emit(self, record):
            log_message = self.format(record)
            self.ui.log_messages.append(log_message)
            
            # Limit to last 100 messages to prevent memory issues
            if len(self.ui.log_messages) > 100:
                self.ui.log_messages.pop(0)
            
            # Update UI in main thread
            if hasattr(self.ui.ui_components, 'log_text') and self.ui.ui_components.log_text:
                self.ui.root.after(0, self.ui.update_log_display)

    def setup_ui(self):
        """Setup the main UI"""
        self.ui_components.setup_ui()

    def update_log_display(self):
        """Update the log display in the UI"""
        def do_update():
            if hasattr(self.ui_components, 'log_text') and self.ui_components.log_text:
                self.ui_components.log_text.config(state='normal')
                self.ui_components.log_text.delete(1.0, tk.END)
                for msg in self.log_messages:
                    self.ui_components.log_text.insert(tk.END, msg + "\n")
                self.ui_components.log_text.see(tk.END)
                self.ui_components.log_text.config(state='disabled')
        
        self.root.after(0, do_update)

    def show_window(self):
        """Show the main window"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def hide_window(self):
        """Hide the main window"""
        self.root.withdraw()

    def exit_application(self):
        """Cleanly exit the application"""
        try:
            self.system_tray.stop()
        except Exception:
            pass
        
        try:
            # Ensure all processes are terminated
            if self.process:
                self.process.terminate()
                self.process = None
        except Exception:
            pass
        
        try:
            self.root.destroy()
        except Exception:
            pass
        
        sys.exit(0)

    def on_closing(self):
        """Handle window closing event"""
        if messagebox.askokcancel("Quit", "Do you want to quit Android Studio?"):
            self.exit_application()

    def update_config(self):
        """Update configuration from UI components"""
        new_config = {
            'mouse': {
                'enabled': self.ui_components.mouse_enabled.get(),
                'movements': self.ui_components.mouse_movements.get(),
                'min_duration': self.ui_components.mouse_min_duration.get(),
                'max_duration': self.ui_components.mouse_max_duration.get(),
                'min_interval': self.ui_components.mouse_min_interval.get(),
                'max_interval': self.ui_components.mouse_max_interval.get(),
                'scrolls': self.ui_components.mouse_scrolls.get(),
                'scroll_sensitivity': self.ui_components.mouse_scroll_sensitivity.get(),
                'hscrolls': self.ui_components.mouse_hscrolls.get(),
                'scroll_min_interval': self.ui_components.mouse_scroll_min_interval.get(),
                'scroll_max_interval': self.ui_components.mouse_scroll_max_interval.get()
            },
            'keyboard': {
                'enabled': self.ui_components.keyboard_enabled.get(),
                'actions': self.ui_components.keyboard_actions.get(),
                'phrases': [p.strip() for p in self.ui_components.keyboard_phrases.get().split(',')],
                'min_interval': self.ui_components.keyboard_min_interval.get(),
                'max_interval': self.ui_components.keyboard_max_interval.get(),
                'dart_enabled': self.ui_components.dart_enabled.get(),
                'dart_lines': self.ui_components.dart_lines.get(),
                'code_writing_enabled': self.ui_components.code_writing_enabled.get(),
                'typing_from_file_enabled': self.ui_components.typing_from_file_enabled.get(),
                'typing_file_path': self.ui_components.typing_file_path.get()
            },
            'browser': {
                'enabled': self.ui_components.browser_enabled.get(),
                'headless': self.ui_components.browser_headless.get(),
                'min_interval': self.ui_components.browser_min_interval.get(),
                'max_interval': self.ui_components.browser_max_interval.get()
            },
            'ui': {
                'dark_mode': self.ui_components.is_dark_mode,
                'auto_restart': self.auto_restart_enabled,
                'idle_timeout_minutes': self.idle_timeout_minutes,
                'minimize_on_start': self.ui_components.minimize_on_start_var.get(),
                'hotkey_control': self.ui_components.hotkey_control_var.get(),
                'notifications_enabled': self.ui_components.notifications_enabled.get()
            }
        }
        
        self.config = new_config
        self.save_config()

    def apply_changes(self):
        """Apply configuration changes"""
        if self.simulation_controls.simulation_running:
            self.update_config()
            self.notify_info("Success", "Changes applied to running simulation.")
        else:
            self.notify_warning("Warning", "No simulation is running. Start the simulation first.")

    def start_simulation(self):
        """Start the simulation"""
        self.simulation_controls.start_simulation()
        self.update_status("🟢 Status: Running")

    def stop_simulation(self):
        """Stop the simulation"""
        self.simulation_controls.stop_simulation()
        self.update_status("🔴 Status: Stopped")

    def update_status(self, status_text):
        """Update the status label"""
        if hasattr(self.ui_components, 'status_label') and self.ui_components.status_label:
            self.ui_components.status_label.config(text=status_text.replace('Simulation', 'Active').replace('simulation', 'active'))

    def toggle_auto_restart(self):
        """Toggle auto-restart functionality"""
        self.auto_restart_enabled = self.ui_components.auto_restart_var.get()
        if 'ui' not in self.config:
            self.config['ui'] = {}
        self.config['ui']['auto_restart'] = self.auto_restart_enabled
        self.save_config()

    def toggle_hotkey_control(self):
        """Toggle hotkey control"""
        hotkey_enabled = self.ui_components.hotkey_control_var.get()
        if 'ui' not in self.config:
            self.config['ui'] = {}
        self.config['ui']['hotkey_control'] = hotkey_enabled
        self.save_config()

    def toggle_notifications(self):
        """Toggle notifications"""
        notifications_enabled = self.ui_components.notifications_enabled.get()
        if 'ui' not in self.config:
            self.config['ui'] = {}
        self.config['ui']['notifications_enabled'] = notifications_enabled
        self.save_config()

    def toggle_minimize_on_start(self):
        """Toggle minimize on start"""
        minimize_enabled = self.ui_components.minimize_on_start_var.get()
        if 'ui' not in self.config:
            self.config['ui'] = {}
        self.config['ui']['minimize_on_start'] = minimize_enabled
        self.save_config()

    def schedule_idle_check(self):
        """Schedule idle timeout check"""
        if self.auto_restart_enabled and self.simulation_controls.simulation_running:
            self.auto_restart_timer = self.root.after(
                self.idle_timeout_minutes * 60 * 1000,  # Convert minutes to milliseconds
                self.check_user_idle_and_restart
            )

    def cancel_auto_restart(self):
        """Cancel auto-restart timer"""
        if self.auto_restart_timer:
            self.root.after_cancel(self.auto_restart_timer)
            self.auto_restart_timer = None

    def check_user_idle_and_restart(self):
        """Check if user is idle and restart if needed"""
        if self.user_is_idle and self.auto_restart_enabled:
            self.simulation_controls.start_simulation()
            self.user_is_idle = False

    def update_idle_timeout(self):
        """Update idle timeout setting"""
        self.idle_timeout_minutes = self.ui_components.idle_timeout_var.get()
        if 'ui' not in self.config:
            self.config['ui'] = {}
        self.config['ui']['idle_timeout_minutes'] = self.idle_timeout_minutes
        self.save_config()

    def reset_idle_timer(self):
        """Reset the idle timer"""
        self.cancel_auto_restart()
        self.user_is_idle = False
        self.schedule_idle_check()

    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with default config to ensure all keys exist
                    default_config = self.get_default_config()
                    return self.merge_configs(default_config, config)
            else:
                # Create default config if file doesn't exist
                config = self.get_default_config()
                self.save_config(config)
                return config
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return self.get_default_config()

    def save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        try:
            # Ensure config directory exists
            config_dir = os.path.dirname(self.config_file)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")

    def merge_configs(self, default_config, user_config):
        """Merge default and user configurations"""
        merged = default_config.copy()
        
        def merge_dict(base, update):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value
        
        merge_dict(merged, user_config)
        return merged

    def notify_info(self, title, message):
        """Show info notification if enabled"""
        if self.config.get('ui', {}).get('notifications_enabled', False):
            from tkinter import messagebox
            messagebox.showinfo(title, message)

    def notify_warning(self, title, message):
        """Show warning notification if enabled"""
        if self.config.get('ui', {}).get('notifications_enabled', False):
            from tkinter import messagebox
            messagebox.showwarning(title, message)

    def notify_error(self, title, message):
        """Show error notification if enabled"""
        if self.config.get('ui', {}).get('notifications_enabled', False):
            from tkinter import messagebox
            messagebox.showerror(title, message)

    def open_url(self, url):
        """Open URL in default browser"""
        import webbrowser
        try:
            webbrowser.open(url)
        except Exception as e:
            self.logger.error(f"Failed to open URL {url}: {e}")

    def check_and_open_github_on_first_run(self):
        """Check if this is the first run and open GitHub if needed"""
        first_run_file = os.path.join(project_root, "config", ".first_run")
        if not os.path.exists(first_run_file):
            try:
                # Create first run marker
                os.makedirs(os.path.dirname(first_run_file), exist_ok=True)
                with open(first_run_file, 'w') as f:
                    f.write("1")
                
                # Open GitHub in browser
                self.open_url("https://github.com/yasirSub/AndroidStudioV1")
            except Exception as e:
                self.logger.error(f"Failed to handle first run: {e}")

    def get_default_config(self):
        """Get default configuration"""
        return {
            'mouse': {
                'enabled': False,
                'movements': 5,
                'min_duration': 0.5,
                'max_duration': 2.0,
                'min_interval': 1.0,
                'max_interval': 5.0,
                'scrolls': 3,
                'scroll_sensitivity': 3,
                'hscrolls': 1,
                'scroll_min_interval': 0.2,
                'scroll_max_interval': 1.0
            },
            'keyboard': {
                'enabled': False,
                'actions': 3,
                'phrases': ['hello', 'test', 'android studio'],
                'min_interval': 2.0,
                'max_interval': 10.0,
                'dart_enabled': True,
                'dart_lines': 700,
                'code_writing_enabled': True,
                'typing_from_file_enabled': False,
                'typing_file_path': ''
            },
            'browser': {
                'enabled': False,
                'headless': True,
                'min_interval': 10.0,
                'max_interval': 30.0
            },
            'ui': {
                'dark_mode': False,
                'auto_restart': True,
                'idle_timeout_minutes': 1,
                'minimize_on_start': True,
                'hotkey_control': True,
                'notifications_enabled': False,
                'pause_after_activity': 3
            }
        }

if __name__ == "__main__":
    import random
    root = tk.Tk()
    app = AndroidStudioUI(root)
    # Minimize to tray on start only if explicitly enabled
    if app.config.get('ui', {}).get('minimize_on_start', False):
        app.logger.info("Minimizing to system tray on start as per configuration.")
        root.after(100, app.system_tray.minimize_to_tray)
    root.mainloop()
