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
        self.root.title("Android Studio v1.0.0")
        self.root.geometry("700x550")  # Larger window for breathing room
        self.root.minsize(600, 500)
        self.root.option_add("*Font", "Arial 11")  # Modern font for all widgets
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
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.ui_components.apply_theme()
        # Global hotkey for pause/resume
        try:
            global_keyboard.add_hotkey('ctrl+shift+p', self.simulation_controls.toggle_simulation_hotkey)
        except Exception:
            pass
        # Set window icon if available
        try:
            self.root.iconbitmap('Android_Studio_icon_(2023).ico')
        except Exception:
            try:
                # Fallback to SVG if ICO conversion is available or handled by another method
                self.root.iconphoto(True, tk.PhotoImage(file='Android_Studio_icon_(2023).svg'))
            except Exception:
                pass
        # Check for first run to open GitHub link
        self.check_and_open_github_on_first_run()

    def migrate_old_files(self):
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
        try:
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', 
                                handlers=[logging.FileHandler(self.log_file)])
        except Exception as e:
            messagebox.showerror("Error", f"Cannot create log file: {e}")
            self.root.destroy()
            sys.exit(1)
        self.logger = logging.getLogger("android_studio")
        self.log_handler = self.LogHandler(self)
        self.logger.addHandler(self.log_handler)

    class LogHandler(logging.Handler):
        def __init__(self, ui):
            super().__init__()
            self.ui = ui

        def emit(self, record):
            log_message = self.format(record)
            self.ui.log_messages.append(log_message)
            if len(self.ui.log_messages) > 100:  # Limit to last 100 messages to prevent memory issues
                self.ui.log_messages.pop(0)
            if hasattr(self.ui.ui_components, 'log_text') and self.ui.ui_components.log_text:
                self.ui.root.after(0, self.ui.update_log_display)

    def setup_ui(self):
        self.ui_components.setup_ui()

    def update_log_display(self):
        # Always update log in the main thread
        def do_update():
            self.ui_components.log_text.delete(1.0, tk.END)
            for msg in self.log_messages:
                self.ui_components.log_text.insert(tk.END, msg + "\n")
            self.ui_components.log_text.see(tk.END)
        self.root.after(0, do_update)

    def show_window(self):
        self.root.deiconify()
        self.root.lift()

    def exit_application(self):
        try:
            self.system_tray.stop()
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass
        try:
            # Ensure all processes are terminated
            if self.process:
                self.process.terminate()
                self.process = None
        except Exception:
            pass
        sys.exit(0)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit Android Studio?"):
            self.exit_application()

    def update_config(self):
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
                'code_writing_enabled': self.ui_components.code_writing_enabled.get()
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
                'minimize_on_start': self.ui_components.minimize_on_start_var.get()
            }
        }
        self.save_config()
        self.config = new_config

    def apply_changes(self):
        if self.simulation_controls.simulation_running:
            self.update_config()
            self.notify_info("Success", "Changes applied to running simulation.")
        else:
            self.notify_warning("Warning", "No simulation is running. Start the simulation first.")

    def start_simulation(self):
        self.simulation_controls.start_simulation()

    def stop_simulation(self):
        self.simulation_controls.stop_simulation()

    def toggle_auto_restart(self):
        self.auto_restart_enabled = self.ui_components.auto_restart_var.get()
        if 'ui' not in self.config:
            self.config['ui'] = {}
        self.config['ui']['auto_restart'] = self.auto_restart_enabled
        self.save_config()
        if not self.auto_restart_enabled and self.auto_restart_timer:
            self.cancel_auto_restart()

    def toggle_hotkey_control(self):
        hotkey_control_enabled = self.ui_components.hotkey_control_var.get()
        if 'ui' not in self.config:
            self.config['ui'] = {}
        self.config['ui']['hotkey_control'] = hotkey_control_enabled
        self.save_config()
        # Notify user about hotkey control status
        status = "enabled" if hotkey_control_enabled else "disabled"
        self.notify_info("Hotkey Control", f"Hotkey control is now {status}. Restart the application to apply changes.")

    def toggle_notifications(self):
        if 'ui' not in self.config:
            self.config['ui'] = {}
        self.config['ui']['notifications_enabled'] = self.ui_components.notifications_enabled.get()
        self.save_config()

    def toggle_minimize_on_start(self):
        if 'ui' not in self.config:
            self.config['ui'] = {}
        self.config['ui']['minimize_on_start'] = self.ui_components.minimize_on_start_var.get()
        self.save_config()

    def schedule_idle_check(self):
        if self.auto_restart_timer:
            self.cancel_auto_restart()
        # Add random jitter for stealth
        jitter = random.randint(-10, 10)  # +/- 10 seconds
        ms = max(10, (self.idle_timeout_minutes * 60 + jitter) * 1000)
        self.logger.info(f"Android Studio will auto-restart after {self.idle_timeout_minutes} min (jitter: {jitter}s) of user inactivity.")
        if self.ui_components.notifications_enabled.get():
            self.notify_info("Auto-Restart", f"Android Studio will auto-restart after {self.idle_timeout_minutes} min of user inactivity unless you disable auto-restart.")
        self.auto_restart_timer = self.root.after(ms, self.check_user_idle_and_restart)
        self.user_is_idle = False

    def cancel_auto_restart(self):
        if self.auto_restart_timer:
            self.root.after_cancel(self.auto_restart_timer)
            self.auto_restart_timer = None
            self.logger.info("Auto-restart canceled.")
            self.notify_info("Auto-Restart", "Auto-restart has been canceled.")

    def check_user_idle_and_restart(self):
        self.auto_restart_timer = None
        if not self.simulation_controls.simulation_running and not self.simulation_controls.user_stopped_simulation:
            self.logger.info("Auto-restarting simulation after user idle period.")
            self.start_simulation()

    def update_idle_timeout(self):
        self.idle_timeout_minutes = self.ui_components.idle_timeout_var.get()
        if 'ui' not in self.config:
            self.config['ui'] = {}
        self.config['ui']['idle_timeout_minutes'] = self.idle_timeout_minutes
        self.save_config()
        if self.auto_restart_timer:
            self.cancel_auto_restart()

    def reset_idle_timer(self):
        self.user_is_idle = False
        if self.auto_restart_timer:
            self.cancel_auto_restart()
        if self.auto_restart_enabled and not self.simulation_controls.simulation_running and not self.simulation_controls.user_stopped_simulation:
            self.schedule_idle_check()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as file:
                config = json.load(file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {e}")
            config = self.get_default_config()
        # Ensure all required keys are present
        default = self.get_default_config()
        for key in default:
            if key not in config:
                config[key] = default[key]
            elif isinstance(default[key], dict):
                for subkey in default[key]:
                    if subkey not in config[key]:
                        config[key][subkey] = default[key][subkey]
        return config

    def save_config(self):
        try:
            with open(self.config_file, 'w') as file:
                json.dump(self.config, file, indent=2)
            messagebox.showinfo("Success", "Configuration saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")

    def notify_info(self, *args, **kwargs):
        if hasattr(self.ui_components, 'notifications_enabled') and self.ui_components.notifications_enabled.get():
            self.root.after(0, lambda: messagebox.showinfo(*args, **kwargs))
    def notify_warning(self, *args, **kwargs):
        if hasattr(self.ui_components, 'notifications_enabled') and self.ui_components.notifications_enabled.get():
            self.root.after(0, lambda: messagebox.showwarning(*args, **kwargs))
    def notify_error(self, *args, **kwargs):
        if hasattr(self.ui_components, 'notifications_enabled') and self.ui_components.notifications_enabled.get():
            self.root.after(0, lambda: messagebox.showerror(*args, **kwargs))
            
    def open_url(self, url):
        import webbrowser
        try:
            webbrowser.open(url)
            self.logger.info(f"Opened URL in browser: {url}")
        except Exception as e:
            self.logger.error(f"Failed to open URL {url}: {e}")
            self.notify_error("Error", f"Failed to open browser: {e}")
            
    def check_and_open_github_on_first_run(self):
        if 'ui' not in self.config:
            self.config['ui'] = {}
        if not self.config['ui'].get('first_run_completed', False):
            self.open_url("https://github.com/yasirSub")
            self.config['ui']['first_run_completed'] = True
            self.save_config()
            self.logger.info("First run detected, opened GitHub repository in browser.")

    def get_default_config(self):
        return {
            'mouse': {
                'enabled': True,
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
                'enabled': True,
                'actions': 3,
                'phrases': [
                    'hello',
                    'working on a project',
                    'checking email',
                    'typing a report'
                ],
                'min_interval': 2.0,
                'max_interval': 10.0,
                'dart_enabled': False,
                'dart_lines': 10,
                'code_writing_enabled': True
            },
            'browser': {
                'enabled': True,
                'headless': True,
                'min_interval': 10.0,
                'max_interval': 30.0
            },
            'ui': {
                'dark_mode': True,
                'hotkey_control': False,  # Stealth default
                'notifications_enabled': False,  # Stealth default
                'idle_timeout_minutes': 1,
                'auto_restart': True,
                'minimize_on_start': True
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
