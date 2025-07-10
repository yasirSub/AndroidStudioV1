import threading
import time
import random
import sys
from tkinter import messagebox
import logging

class SimulationControls:
    def __init__(self, app):
        self.app = app
        self.simulation_running = False
        self.simulation_thread = None
        self.user_activity_listener = None
        self.user_stopped_simulation = False
        self.resume_timer = None
        self.paused = False  # <-- Add paused flag
        self.logger = logging.getLogger("android_studio")

    def start_simulation(self):
        if not self.simulation_running:
            try:
                self.simulation_running = True
                self.paused = False  # Not paused when starting
                self.app.ui_components.status_label.config(text="Status: Simulation Running")
                self.app.system_tray.update_status("running")
                self.logger.info("Starting simulation...")
                self.user_stopped_simulation = False
                self.start_user_activity_listener()
                self.simulation_thread = threading.Thread(target=self.run_simulation, daemon=True)
                self.simulation_thread.start()
                self.app.notify_info("Success", "Simulation started.")
                self.app.root.after(200, self.app.system_tray.minimize_to_tray)
            except Exception as e:
                self.simulation_running = False
                self.paused = False
                self.app.ui_components.status_label.config(text="Status: Simulation Stopped")
                self.app.system_tray.update_status("stopped")
                self.logger.error(f"Failed to start simulation: {e}")
                self.app.notify_error("Error", f"Failed to start simulation: {e}")
        else:
            self.app.notify_warning("Warning", "Simulation is already running.")

    def stop_simulation(self, schedule_restart=True):
        if self.simulation_running:
            self.simulation_running = False
            self.paused = False
            self.app.ui_components.status_label.config(text="Status: Simulation Stopped")
            self.app.system_tray.update_status("stopped")
            self.logger.info("Simulation stopped.")
            self.user_stopped_simulation = not schedule_restart
            self.stop_user_activity_listener()
            if self.simulation_thread and self.simulation_thread.is_alive():
                self.simulation_thread.join(timeout=2)
            self.app.notify_info("Success", "Simulation stopped.")
            if schedule_restart and self.app.auto_restart_enabled and not self.user_stopped_simulation:
                self.app.schedule_idle_check()
        else:
            self.app.notify_warning("Warning", "No simulation is running.")

    def start_user_activity_listener(self):
        try:
            from pynput import mouse as pynput_mouse, keyboard as pynput_keyboard  # type: ignore
        except ImportError:
            self.logger.warning("pynput not installed. User activity detection will not work.")
            return
        self.stop_user_activity_listener()
        def on_mouse_move(x, y):
            self.logger.info("User mouse activity detected. Pausing simulation and resetting resume timer.")
            self.handle_user_activity()
            return None
        def on_key_press(key):
            self.logger.info("User keyboard activity detected. Pausing simulation and resetting resume timer.")
            self.handle_user_activity()
            return None
        self.user_activity_listener = {
            'mouse': pynput_mouse.Listener(on_move=on_mouse_move),
            'keyboard': pynput_keyboard.Listener(on_press=on_key_press)
        }
        self.user_activity_listener['mouse'].start()
        self.user_activity_listener['keyboard'].start()

    def stop_user_activity_listener(self):
        if self.user_activity_listener:
            for listener in self.user_activity_listener.values():
                try:
                    listener.stop()
                except Exception:
                    pass
            self.user_activity_listener = None

    def handle_user_activity(self):
        # Pause simulation if running
        if self.simulation_running and not self.paused:
            self.paused = True
            self.app.system_tray.update_status("paused")
            self.app.ui_components.status_label.config(text="Status: Paused (User Activity)")
            self.logger.info("User activity detected. Pausing simulation for 3 seconds.")
        # Cancel any existing resume timer
        if self.resume_timer:
            self.app.root.after_cancel(self.resume_timer)
            self.resume_timer = None
        # Start a new 3-second timer to resume simulation
        self.resume_timer = self.app.root.after(3000, self.resume_simulation)

    def resume_simulation(self):
        self.resume_timer = None
        if self.simulation_running and self.paused:
            self.paused = False
            self.app.system_tray.update_status("running")
            self.app.ui_components.status_label.config(text="Status: Simulation Running")
            self.logger.info("No user activity for 3 seconds. Resuming simulation.")

    def run_simulation(self):
        last_config_load = 0
        while self.simulation_running:
            if self.paused:
                time.sleep(0.1)
                continue
            try:
                # Defensive: ensure config has all required keys
                if not self.app.config or 'mouse' not in self.app.config or 'keyboard' not in self.app.config or 'browser' not in self.app.config:
                    self.logger.warning("Config missing required keys, resetting to default.")
                    self.app.config = self.app.get_default_config()
                current_time = time.time()
                if current_time - last_config_load > 300:  # Reload config every 5 minutes
                    self.app.config = self.app.load_config()
                    last_config_load = current_time
                    self.logger.info("Configuration reloaded.")
                if self.app.config['mouse']['enabled']:
                    try:
                        import pyautogui  # type: ignore
                    except ImportError:
                        self.logger.error("pyautogui not installed. Mouse simulation will not work.")
                        break
                    screen_width, screen_height = pyautogui.size()
                    self.logger.info("Starting mouse simulation...")
                    for _ in range(self.app.config['mouse']['movements']):
                        if not self.simulation_running:
                            break
                        while self.paused and self.simulation_running:
                            time.sleep(0.1)
                        start_x, start_y = pyautogui.position()
                        end_x = random.randint(int(screen_width * 0.2), int(screen_width * 0.8))
                        end_y = random.randint(int(screen_height * 0.2), int(screen_height * 0.8))
                        control_x = random.randint(min(start_x, end_x), max(start_x, end_x))
                        control_y = random.randint(min(start_y, end_y), max(start_y, end_y))
                        duration = random.uniform(self.app.config['mouse']['min_duration'], self.app.config['mouse']['max_duration'])
                        steps = random.randint(5, 10)
                        for t in range(steps + 1):
                            if not self.simulation_running:
                                break
                            while self.paused and self.simulation_running:
                                time.sleep(0.1)
                            t_norm = t / steps
                            x = (1 - t_norm)**2 * start_x + 2 * (1 - t_norm) * t_norm * control_x + t_norm**2 * end_x
                            y = (1 - t_norm)**2 * start_y + 2 * (1 - t_norm) * t_norm * control_y + t_norm**2 * end_y
                            pyautogui.moveTo(int(x), int(y), duration=duration/steps)
                        for _ in range(random.randint(0, 5)):
                            if not self.simulation_running:
                                break
                            while self.paused and self.simulation_running:
                                time.sleep(0.1)
                            x_small = end_x + random.randint(-30, 30)
                            y_small = end_y + random.randint(-30, 30)
                            pyautogui.moveTo(x_small, y_small, duration=random.uniform(0.1, 0.4))
                        time.sleep(random.uniform(0.1, 0.5))
                        # Simulate vertical scrolls
                        for _ in range(self.app.config['mouse'].get('scrolls', 3)):
                            if not self.simulation_running:
                                break
                            while self.paused and self.simulation_running:
                                time.sleep(0.1)
                            scroll_amount = random.choice([-1, 1]) * self.app.config['mouse'].get('scroll_sensitivity', 3)
                            pyautogui.scroll(scroll_amount)
                            time.sleep(random.uniform(self.app.config['mouse'].get('scroll_min_interval', 0.2), self.app.config['mouse'].get('scroll_max_interval', 1.0)))
                        # Simulate horizontal scrolls
                        for _ in range(self.app.config['mouse'].get('hscrolls', 1)):
                            if not self.simulation_running:
                                break
                            while self.paused and self.simulation_running:
                                time.sleep(0.1)
                            hscroll_amount = random.choice([-1, 1]) * self.app.config['mouse'].get('scroll_sensitivity', 3)
                            pyautogui.hscroll(hscroll_amount)
                            time.sleep(random.uniform(self.app.config['mouse'].get('scroll_min_interval', 0.2), self.app.config['mouse'].get('scroll_max_interval', 1.0)))
                    self.logger.info("Mouse simulation cycle completed.")
                if self.app.config['keyboard']['enabled']:
                    try:
                        import pyautogui  # type: ignore
                    except ImportError:
                        self.logger.error("pyautogui not installed. Keyboard simulation will not work.")
                        break
                    self.logger.info("Starting keyboard simulation...")
                    for _ in range(self.app.config['keyboard']['actions']):
                        if not self.simulation_running:
                            break
                        while self.paused and self.simulation_running:
                            time.sleep(0.1)
                        if self.app.ui_components.code_writing_enabled.get():
                            # Write a marker and some code
                            pyautogui.write("--------------------------------\n")
                            code_snippet = "def example_function():\n    print('This is a test code snippet.')\n    return True\n"
                            pyautogui.write(code_snippet)
                            time.sleep(random.uniform(2.0, 4.0))  # Wait before erasing
                            # Erase the written code
                            pyautogui.hotkey('ctrl', 'a')  # Select all
                            time.sleep(0.5)
                            pyautogui.press('backspace')  # Delete selected text
                        time.sleep(random.uniform(0.2, 1.0))
                        for _ in range(int(random.uniform(self.app.config['keyboard']['min_interval'], self.app.config['keyboard']['max_interval']) * 10)):
                            if not self.simulation_running:
                                break
                            while self.paused and self.simulation_running:
                                time.sleep(0.1)
                            time.sleep(0.1)
                    self.logger.info("Keyboard simulation cycle completed.")
                if self.app.config['browser']['enabled']:
                    self.logger.info("Starting browser simulation...")
                    try:
                        from selenium import webdriver  # type: ignore
                        from selenium.webdriver.chrome.options import Options  # type: ignore
                        from selenium.webdriver.common.by import By  # type: ignore
                        from selenium.webdriver.common.keys import Keys  # type: ignore
                        from selenium.webdriver.common.action_chains import ActionChains  # type: ignore
                        chrome_options = Options()
                        if self.app.config['browser']['headless']:
                            chrome_options.add_argument("--headless")
                        browser_version = f"{random.randint(90, 120)}.0.{random.randint(4000, 5000)}.{random.randint(100, 200)}"
                        os_platforms = [
                            "Windows NT 10.0; Win64; x64",
                            "Windows NT 6.1; Win64; x64",
                            "Macintosh; Intel Mac OS X 10_15_7",
                            "Macintosh; Intel Mac OS X 11_2_3"
                        ]
                        os_platform = random.choice(os_platforms)
                        user_agent = f"Mozilla/5.0 ({os_platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{browser_version} Safari/537.36"
                        chrome_options.add_argument(f"user-agent={user_agent}")
                        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                        chrome_options.add_experimental_option('useAutomationExtension', False)
                        chrome_options.add_argument("--disable-extensions")
                        chrome_options.add_argument("--disable-gpu")
                        chrome_options.add_argument("--no-sandbox")
                        if not self.app.config['browser']['headless']:
                            width = random.randint(800, 1920)
                            height = random.randint(600, 1080)
                            chrome_options.add_argument(f"--window-size={width},{height}")
                            self.logger.info(f"Setting browser window size to {width}x{height}")
                        chrome_options.add_argument("--disable-webgl")
                        chrome_options.add_argument("--disable-canvas-aa")
                        chrome_options.add_argument("--disable-2d-canvas-clip-aa")
                        driver = webdriver.Chrome(options=chrome_options)
                        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                        # ... rest of browser simulation ...
                        driver.quit()
                    except ImportError:
                        self.logger.error("selenium not installed. Browser simulation will not work.")
                    except Exception as e:
                        self.logger.error(f"Error in browser simulation: {e}")
                    for _ in range(int(random.uniform(self.app.config['browser']['min_interval'], self.app.config['browser']['max_interval']) * 10)):
                        if not self.simulation_running:
                            break
                        time.sleep(0.1)
                pause = random.uniform(5, 15)
                self.logger.info(f"Pausing for {pause:.2f} seconds before next cycle.")
                for _ in range(int(pause * 10)):
                    if not self.simulation_running:
                        break
                    time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Error in simulation: {e}")
                time.sleep(1)

    def toggle_simulation_hotkey(self):
        if self.simulation_running:
            self.stop_simulation(schedule_restart=False)
            self.logger.info("Simulation paused by hotkey.")
        else:
            self.start_simulation()
            self.logger.info("Simulation resumed by hotkey.")
