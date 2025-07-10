import sys
import os
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pkg_resources")

# Add the project root directory to sys.path to ensure imports work correctly
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the main application class
from core.ui import AndroidStudioUI
import tkinter as tk
import sys
import os
from logic.config_manager import ConfigManager

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Android Studio")
    app = AndroidStudioUI(root)
    # Minimize to tray on start only if explicitly enabled
    if app.config.get('ui', {}).get('minimize_on_start', False):
        app.logger.info("Minimizing to system tray on start as per configuration.")
        root.after(100, app.system_tray.minimize_to_tray)
    # Auto-start simulation if enabled in config
    if app.config.get('ui', {}).get('auto_start_simulation', False):
        app.logger.info("Auto-starting simulation as per configuration.")
        root.after(200, app.start_simulation)
    root.mainloop()
