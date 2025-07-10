import pyautogui  # type: ignore
pyautogui.FAILSAFE = False  # Disable fail-safe to prevent interruption
import time
import random
import json
import sys
import os
from logic.config_manager import ConfigManager
import logging
from datetime import datetime
import keyboard  # type: ignore

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', 
                    handlers=[logging.FileHandler("android_studio.log"), logging.StreamHandler()])
logger = logging.getLogger(__name__)

# Load configuration
def load_config():
    try:
        with open('config/anoid.json', 'r') as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return {}

# Simulate mouse movement with human-like patterns
def simulate_mouse(config):
    try:
        screen_width, screen_height = pyautogui.size()
        logger.info("Starting mouse simulation...")
        for _ in range(config['mouse']['movements']):
            # Simulate more natural movement by favoring center of screen
            x = random.randint(int(screen_width * 0.25), int(screen_width * 0.75))
            y = random.randint(int(screen_height * 0.25), int(screen_height * 0.75))
            duration = random.uniform(config['mouse']['min_duration'], config['mouse']['max_duration'])
            pyautogui.moveTo(x, y, duration=duration)
            # Occasionally click or double-click to mimic interaction
            if random.random() < 0.25:
                pyautogui.click()
            elif random.random() < 0.1:
                pyautogui.doubleClick()
            # Random small movements to mimic cursor hovering
            for _ in range(random.randint(0, 3)):
                x_small = x + random.randint(-20, 20)
                y_small = y + random.randint(-20, 20)
                pyautogui.moveTo(x_small, y_small, duration=random.uniform(0.1, 0.3))
            time.sleep(random.uniform(config['mouse']['min_interval'], config['mouse']['max_interval']))
        logger.info("Mouse simulation cycle completed.")
    except Exception as e:
        logger.error(f"Error in mouse simulation: {e}")

# Simulate keyboard input with human-like variability
def simulate_keyboard(config):
    try:
        logger.info("Starting keyboard simulation...")
        for _ in range(config['keyboard']['actions']):
            phrase = random.choice(config['keyboard']['phrases'])
            # Add occasional typos to mimic human error
            if random.random() < 0.15:
                typo_index = random.randint(0, len(phrase) - 1)
                phrase = phrase[:typo_index] + random.choice('abcdefghijklmnopqrstuvwxyz') + phrase[typo_index + 1:]
                pyautogui.write(phrase, interval=random.uniform(0.05, 0.2))
                time.sleep(random.uniform(0.5, 1.5))
                pyautogui.press('backspace', presses=len(phrase) - typo_index)
                pyautogui.write(phrase[typo_index:], interval=random.uniform(0.05, 0.2))
            else:
                pyautogui.write(phrase, interval=random.uniform(0.05, 0.2))
            # Randomly press enter or other keys
            if random.random() < 0.6:
                pyautogui.press('enter')
            elif random.random() < 0.3:
                pyautogui.press(random.choice(['backspace', 'space', 'tab']))
            else:
                pyautogui.hotkey('ctrl', random.choice(['c', 'v', 'a']))
            time.sleep(random.uniform(config['keyboard']['min_interval'], config['keyboard']['max_interval']))
        logger.info("Keyboard simulation cycle completed.")
    except Exception as e:
        logger.error(f"Error in keyboard simulation: {e}")

# Remove simulate_browser and all browser simulation logic
# Remove browser simulation from run_simulation

def run_simulation(config, last_config_load):
    try:
        # Reload config every 5 minutes in case it was updated via UI
        current_time = time.time()
        if current_time - last_config_load > 300:
            config = load_config()
            last_config_load = current_time
            logger.info("Configuration reloaded.")
        if config['mouse']['enabled']:
            simulate_mouse(config)
        if config['keyboard']['enabled']:
            simulate_keyboard(config)
        #if config['browser']['enabled']:
        #    simulate_browser(config)
        # Random pause between cycles to avoid predictable patterns
        pause = random.uniform(5, 15)
        logger.info(f"Pausing for {pause:.2f} seconds before next cycle.")
        time.sleep(pause)
    except Exception as e:
        logger.error(f"Unexpected error in simulation loop: {e}")
        time.sleep(10)  # Wait before retrying to avoid rapid error loops
    return config, last_config_load

def main():
    logger.info("Android Studio simulation control initialized.")
    last_config_load = 0
    config = load_config()
    if not config:
        logger.error("Configuration is empty or failed to load. Exiting.")
        sys.exit(1)
    
    simulation_running = False
    simulation_thread = None
    
    def start_simulation():
        nonlocal simulation_running, config, last_config_load, simulation_thread
        if not simulation_running:
            logger.info("Starting simulation with Ctrl + `")
            simulation_running = True
            while simulation_running:
                config, last_config_load = run_simulation(config, last_config_load)
        else:
            logger.info("Simulation already running.")
    
    def stop_simulation():
        nonlocal simulation_running
        if simulation_running:
            logger.info("Stopping simulation with Ctrl + =")
            simulation_running = False
        else:
            logger.info("Simulation is not running.")
    
    # Register only ALT+` for hide/show tray
    hotkey_control_enabled = config.get('ui', {}).get('hotkey_control', True)
    if hotkey_control_enabled:
        # ALT+`: Hide and show tray (toggle)
        tray_hidden = False
        def toggle_tray():
            nonlocal tray_hidden
            tray_hidden = not tray_hidden
            if tray_hidden:
                logger.info("Hiding to tray with ALT+`")
                # Implement tray hide logic if running with UI
            else:
                logger.info("Showing from tray with ALT+`")
                # Implement tray show logic if running with UI
        keyboard.add_hotkey('alt+`', toggle_tray)
        logger.info("Hotkey registered: ALT+` (hide/show tray)")
    else:
        logger.info("Hotkey control is disabled in configuration. Use UI to control tray.")
    
    # Keep the script running to listen for hotkeys or until user exits
    keyboard.wait('esc')  # This will keep the script running until 'esc' is pressed to exit completely
    logger.info("Android Studio terminated by user.")

if __name__ == "__main__":
    main()
