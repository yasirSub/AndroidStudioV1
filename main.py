import sys
import os
import argparse
import logging
import time
import threading
import psutil
from core.engine import SimulationEngine
from logic.config_manager import ConfigManager
from core.system_tray import SystemTray

def setup_cli_logging(log_file):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("android_studio")

def run_cli_mode(config_manager, logger):
    logger.info("Starting in CLI mode...")
    
    engine = SimulationEngine(config_manager, logger)
    
    # We still want the tray icon if possible, but without a full Tkinter loop
    # pystray can run its own loop.
    tray = SystemTray(None) # Pass None to decouple from UI
    tray.app = type('obj', (object,), {'start_simulation': engine.start, 
                                     'stop_simulation': engine.stop,
                                     'toggle_pause': engine.toggle_pause,
                                     'exit_application': sys.exit,
                                     'show_window': lambda: logger.info("UI is disabled in CLI mode.")})
    
    engine.set_status_callback(tray.update_status)
    
    # Auto-start if configured
    config = config_manager.get_config()
    if config.get('ui', {}).get('auto_start_simulation', True):
        engine.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping...")
        engine.stop()
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Android Studio (Anoid) Utility")
    parser.add_argument("--cli", action="store_true", help="Run in terminal mode without UI")
    parser.add_argument("--gui", action="store_true", help="Run with Graphical User Interface")
    args = parser.parse_args()

    # Handle PyInstaller path resolution
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        project_root = sys._MEIPASS
    else:
        project_root = os.path.dirname(os.path.abspath(__file__))
    
    config_manager = ConfigManager()
    config_dir = os.path.join(project_root, "config")
    os.makedirs(config_dir, exist_ok=True)
    
    # --- SINGLE INSTANCE CHECK (Takeover Mode) ---
    lock_file = os.path.join(config_dir, "anoid.pid")
    current_pid = os.getpid()
    
    if os.path.exists(lock_file):
        try:
            with open(lock_file, "r") as f:
                old_pid = int(f.read().strip())
            
            if psutil.pid_exists(old_pid) and old_pid != current_pid:
                # User requested: "one will stop and another will run"
                old_proc = psutil.Process(old_pid)
                # Check if it's actually our app (simple check)
                if "python" in old_proc.name().lower() or "androidstudiov1" in old_proc.name().lower():
                    print(f"Terminating existing instance (PID: {old_pid})...")
                    try:
                        old_proc.terminate()
                        old_proc.wait(timeout=2)
                    except psutil.TimeoutExpired:
                        print(f"Force-killing existing instance (PID: {old_pid})...")
                        old_proc.kill()
                        old_proc.wait(timeout=2)
        except Exception as e:
            print(f"Single instance check failed: {e}")
            
    # Write current PID
    with open(lock_file, "w") as f:
        f.write(str(current_pid))
    # ----------------------------------------------

    # Auto-clear massive log file (> 1MB) on startup to prevent slowdowns and freezing
    log_file_path = os.path.join(config_dir, "anoid.log")
    if os.path.exists(log_file_path) and os.path.getsize(log_file_path) > 1 * 1024 * 1024:
        try:
            with open(log_file_path, "w", encoding="utf-8") as f:
                f.write("")
        except Exception:
            pass

    logger = setup_cli_logging(log_file_path)

    # If neither flag is set, check config or default to GUI
    # But user specifically asked for terminal mode, so I'll make it smart.
    
    if args.cli:
        run_cli_mode(config_manager, logger)
    elif args.gui:
        from core.ui import AndroidStudioUI
        import tkinter as tk
        root = tk.Tk()
        app = AndroidStudioUI(root)
        root.mainloop()
    else:
        # Default behavior: GUI if possible, CLI if not or if configured
        try:
            from core.ui import AndroidStudioUI
            import tkinter as tk
            root = tk.Tk()
            app = AndroidStudioUI(root)
            root.mainloop()
        except Exception as e:
            logger.warning(f"Could not start GUI ({e}). Falling back to CLI.")
            run_cli_mode(config_manager, logger)

if __name__ == "__main__":
    main()
