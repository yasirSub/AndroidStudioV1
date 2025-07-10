import pyautogui  # type: ignore
pyautogui.FAILSAFE = False  # Disable fail-safe to prevent interruption
import time
import random
import json
import sys
import logging
from datetime import datetime
import selenium  # type: ignore
from selenium import webdriver  # type: ignore
from selenium.webdriver.chrome.options import Options  # type: ignore
from selenium.webdriver.common.by import By  # type: ignore
from selenium.webdriver.common.keys import Keys  # type: ignore
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

# Simulate browser activity with varied interactions
def simulate_browser(config):
    try:
        logger.info("Starting browser simulation...")
        chrome_options = Options()
        if config['browser']['headless']:
            chrome_options.add_argument("--headless")
        # Rotate user-agent to avoid detection
        chrome_options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(90, 120)}.0.{random.randint(0, 9999)}.{random.randint(0, 999)} Safari/537.36")
        # Additional arguments to mimic real browser
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        driver = webdriver.Chrome(options=chrome_options)
        # List of URLs and search terms for varied activity
        activities = [
            {"url": "https://www.google.com", "action": "search", "terms": ["latest news", "weather today", "python tutorial", "tech trends"]},
            {"url": "https://www.wikipedia.org", "action": "browse", "terms": ["History", "Technology", "Science"]},
            {"url": "https://www.youtube.com", "action": "browse", "terms": ["funny videos", "how to code", "music"]}
        ]
        activity = random.choice(activities)
        driver.get(activity["url"])
        time.sleep(random.uniform(2, 4))
        if activity["action"] == "search":
            try:
                search_box = driver.find_element(By.NAME, "q")
                search_box.send_keys(random.choice(activity["terms"]))
                search_box.send_keys(Keys.RETURN)
                time.sleep(random.uniform(3, 6))
                # Simulate clicking on a result
                links = driver.find_elements(By.TAG_NAME, "a")
                if links:
                    random.choice(links[:10]).click()
                    time.sleep(random.uniform(2, 5))
            except Exception as e:
                logger.error(f"Error interacting with search elements: {e}")
        elif activity["action"] == "browse":
            try:
                search_box = driver.find_element(By.ID, "searchInput") if "wikipedia" in activity["url"].lower() else driver.find_element(By.ID, "search")
                search_box.send_keys(random.choice(activity["terms"]))
                search_box.send_keys(Keys.RETURN)
                time.sleep(random.uniform(3, 7))
            except Exception as e:
                logger.error(f"Error interacting with browse elements: {e}")
        driver.quit()
        logger.info("Browser simulation cycle completed.")
        time.sleep(random.uniform(config['browser']['min_interval'], config['browser']['max_interval']))
    except Exception as e:
        logger.error(f"Error in browser simulation: {e}")

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
        if config['browser']['enabled']:
            simulate_browser(config)
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
    
    # Register hotkeys only if enabled in configuration
    hotkey_control_enabled = config.get('ui', {}).get('hotkey_control', True)
    if hotkey_control_enabled:
        keyboard.add_hotkey('ctrl+`', start_simulation)
        keyboard.add_hotkey('ctrl+=', stop_simulation)
        logger.info("Hotkeys registered (Ctrl + ` to start, Ctrl + = to stop). Waiting for user input...")
    else:
        logger.info("Hotkey control is disabled in configuration. Use UI to start/stop simulation.")
    
    # Keep the script running to listen for hotkeys or until user exits
    keyboard.wait('esc')  # This will keep the script running until 'esc' is pressed to exit completely
    logger.info("Android Studio terminated by user.")

if __name__ == "__main__":
    main()
