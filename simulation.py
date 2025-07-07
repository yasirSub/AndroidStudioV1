import time
import random
import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import logging

class Simulation:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.simulation_running = False

    def run_simulation(self):
        last_config_load = 0
        while self.simulation_running:
            try:
                current_time = time.time()
                if current_time - last_config_load > 300:  # Reload config every 5 minutes
                    # Assuming config is updated externally if needed
                    last_config_load = current_time
                    self.logger.info("Configuration reloaded.")
                if self.config['mouse']['enabled']:
                    screen_width, screen_height = pyautogui.size()
                    self.logger.info("Starting mouse simulation...")
                    for _ in range(self.config['mouse']['movements']):
                        # Use a more natural movement pattern with bezier-like curves
                        start_x, start_y = pyautogui.position()
                        end_x = random.randint(int(screen_width * 0.2), int(screen_width * 0.8))
                        end_y = random.randint(int(screen_height * 0.2), int(screen_height * 0.8))
                        control_x = random.randint(min(start_x, end_x), max(start_x, end_x))
                        control_y = random.randint(min(start_y, end_y), max(start_y, end_y))
                        duration = random.uniform(self.config['mouse']['min_duration'], self.config['mouse']['max_duration'])
                        
                        # Simulate a curved path for more human-like movement
                        steps = random.randint(5, 10)
                        for t in range(steps + 1):
                            t = t / steps
                            x = (1 - t)**2 * start_x + 2 * (1 - t) * t * control_x + t**2 * end_x
                            y = (1 - t)**2 * start_y + 2 * (1 - t) * t * control_y + t**2 * end_y
                            pyautogui.moveTo(int(x), int(y), duration=duration/steps)
                        
                        # Randomly decide to click, double-click, or right-click
                        action_chance = random.random()
                        if action_chance < 0.3:
                            pyautogui.click()
                            self.logger.info("Performed a click.")
                        elif action_chance < 0.4:
                            pyautogui.doubleClick()
                            self.logger.info("Performed a double-click.")
                        elif action_chance < 0.45:
                            pyautogui.rightClick()
                            self.logger.info("Performed a right-click.")
                        
                        # Random small movements to mimic cursor hovering or reading
                        for _ in range(random.randint(0, 5)):
                            x_small = end_x + random.randint(-30, 30)
                            y_small = end_y + random.randint(-30, 30)
                            pyautogui.moveTo(x_small, y_small, duration=random.uniform(0.1, 0.4))
                        
                        # Introduce random micro-pauses to mimic human hesitation
                        time.sleep(random.uniform(0.1, 0.5))
                        time.sleep(random.uniform(self.config['mouse']['min_interval'], self.config['mouse']['max_interval']))
                    self.logger.info("Mouse simulation cycle completed.")
                if self.config['keyboard']['enabled']:
                    self.logger.info("Starting keyboard simulation...")
                    for _ in range(self.config['keyboard']['actions']):
                        if self.config['keyboard']['dart_enabled']:
                            # Simulate typing Dart code
                            dart_code_snippets = [
                                "void main() {\n  print('Hello, World!');\n}",
                                "class MyApp extends StatelessWidget {\n  @override\n  Widget build(BuildContext context) {\n    return MaterialApp(\n      home: Scaffold(\n        appBar: AppBar(title: Text('My App')),\n        body: Center(child: Text('Welcome')),\n      ),\n    );\n  }\n}",
                                "Future<String> fetchData() async {\n  await Future.delayed(Duration(seconds: 2));\n  return 'Data fetched';\n}",
                                "List<int> numbers = [1, 2, 3, 4, 5];\nint sum = numbers.reduce((a, b) => a + b);",
                                "import 'package:flutter/material.dart';\nvoid main() => runApp(MyApp());",
                                "enum Status { LOADING, SUCCESS, ERROR }\nStatus currentStatus = Status.LOADING;",
                                "Map<String, dynamic> user = {\n  'name': 'John',\n  'age': 30,\n  'isActive': true\n};",
                                "Stream<int> countStream() async* {\n  for (int i = 1; i <= 5; i++) {\n    yield i;\n    await Future.delayed(Duration(seconds: 1));\n  }\n}",
                                "Widget _buildItem(BuildContext context, int index) {\n  return ListTile(\n    title: Text('Item $index'),\n    onTap: () => print('Tapped item $index'),\n  );\n}",
                                "final TextEditingController _controller = TextEditingController();\nString getText() => _controller.text;"
                            ]
                            self.logger.info("Simulating Dart code typing...")
                            code_snippet = random.choice(dart_code_snippets)
                            lines = code_snippet.split('\n')
                            for i in range(min(len(lines), self.config['keyboard']['dart_lines'])):
                                line = lines[i]
                                for char in line:
                                    pyautogui.write(char)
                                    time.sleep(random.uniform(0.03, 0.1))
                                pyautogui.press('enter')
                                time.sleep(random.uniform(0.1, 0.3))
                            # Simulate scrolling after typing
                            pyautogui.scroll(-random.randint(100, 300))
                            time.sleep(random.uniform(0.5, 1.5))
                            pyautogui.scroll(random.randint(50, 150))
                            self.logger.info("Dart code simulation cycle completed.")
                        else:
                            phrase = random.choice(self.config['keyboard']['phrases'])
                            # Add occasional typos with correction for human-like behavior
                            if random.random() < 0.2:
                                typo_index = random.randint(0, len(phrase) - 1)
                                typo_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                                typo_phrase = phrase[:typo_index] + typo_char + phrase[typo_index + 1:]
                                pyautogui.write(typo_phrase, interval=random.uniform(0.05, 0.15))
                                time.sleep(random.uniform(0.3, 1.2))
                                pyautogui.press('backspace', presses=len(typo_phrase) - typo_index)
                                pyautogui.write(phrase[typo_index:], interval=random.uniform(0.05, 0.15))
                                self.logger.info("Simulated a typo and correction.")
                            else:
                                pyautogui.write(phrase, interval=random.uniform(0.05, 0.15))
                            
                            # Randomly press enter, other keys, or combinations
                            action_chance = random.random()
                            if action_chance < 0.5:
                                pyautogui.press('enter')
                            elif action_chance < 0.7:
                                pyautogui.press(random.choice(['backspace', 'space', 'tab', 'delete']))
                            elif action_chance < 0.85:
                                pyautogui.hotkey('ctrl', random.choice(['c', 'v', 'a', 'x']))
                                self.logger.info("Simulated a keyboard shortcut.")
                            else:
                                # Simulate random key combinations for complexity
                                modifiers = random.sample(['ctrl', 'alt', 'shift'], random.randint(0, 2))
                                if modifiers:
                                    keys = modifiers + [random.choice(['f1', 'f2', 'f3', 'f4', 'f5', 'tab', 'esc'])]
                                    pyautogui.hotkey(*keys)
                                    self.logger.info(f"Simulated complex key combo: {keys}")
                            
                            # Introduce random pauses to mimic thinking or reading
                            time.sleep(random.uniform(0.2, 1.0))
                        time.sleep(random.uniform(self.config['keyboard']['min_interval'], self.config['keyboard']['max_interval']))
                    self.logger.info("Keyboard simulation cycle completed.")
                if self.config['browser']['enabled']:
                    self.logger.info("Starting browser simulation...")
                    chrome_options = Options()
                    if self.config['browser']['headless']:
                        chrome_options.add_argument("--headless")
                    
                    # Rotate user-agents with detailed versioning for realism
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
                    self.logger.info(f"Using user-agent: {user_agent}")
                    
                    # Advanced anti-detection settings
                    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                    chrome_options.add_experimental_option('useAutomationExtension', False)
                    chrome_options.add_argument("--disable-extensions")
                    chrome_options.add_argument("--disable-gpu")
                    chrome_options.add_argument("--no-sandbox")
                    
                    # Randomize window size for non-headless mode to mimic different devices
                    if not self.config['browser']['headless']:
                        width = random.randint(800, 1920)
                        height = random.randint(600, 1080)
                        chrome_options.add_argument(f"--window-size={width},{height}")
                        self.logger.info(f"Setting browser window size to {width}x{height}")
                    
                    # Additional browser fingerprinting evasion
                    chrome_options.add_argument("--disable-webgl")
                    chrome_options.add_argument("--disable-canvas-aa")
                    chrome_options.add_argument("--disable-2d-canvas-clip-aa")
                    
                    driver = webdriver.Chrome(options=chrome_options)
                    
                    # Execute JavaScript to spoof navigator properties
                    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                    
                    # List of activities with varied behaviors
                    activities = [
                        {"url": "https://www.google.com", "action": "search", "terms": ["latest news", "weather today", "python tutorial", "tech trends", "best movies 2023", "local events"], "scroll": True, "clicks": 2},
                        {"url": "https://www.wikipedia.org", "action": "browse", "terms": ["History", "Technology", "Science", "World War II", "Artificial Intelligence"], "scroll": True, "clicks": 1},
                        {"url": "https://www.youtube.com", "action": "browse", "terms": ["funny videos", "how to code", "music playlist", "cooking recipes", "travel vlogs"], "scroll": True, "clicks": 3},
                        {"url": "https://www.reddit.com", "action": "browse", "terms": ["funny", "technology", "askreddit", "memes"], "scroll": True, "clicks": 2},
                        {"url": "https://www.nytimes.com", "action": "read", "terms": [], "scroll": True, "clicks": 1}
                    ]
                    activity = random.choice(activities)
                    self.logger.info(f"Navigating to {activity['url']} with action: {activity['action']}")
                    driver.get(activity["url"])
                    time.sleep(random.uniform(2, 5))
                    
                    # Perform action based on activity type
                    if activity["action"] == "search" and activity["terms"]:
                        search_box = driver.find_element(By.NAME, "q")
                        search_term = random.choice(activity["terms"])
                        # Simulate typing with random pauses
                        for char in search_term:
                            search_box.send_keys(char)
                            time.sleep(random.uniform(0.05, 0.2))
                        search_box.send_keys(Keys.RETURN)
                        time.sleep(random.uniform(3, 6))
                        # Simulate clicking on results
                        links = driver.find_elements(By.TAG_NAME, "a")
                        valid_links = [link for link in links if link.is_displayed() and link.get_attribute("href")]
                        for _ in range(min(activity["clicks"], len(valid_links))):
                            if valid_links:
                                link_to_click = random.choice(valid_links[:10])
                                ActionChains(driver).move_to_element(link_to_click).click().perform()
                                time.sleep(random.uniform(2, 5))
                                driver.back()
                                time.sleep(random.uniform(1, 3))
                                valid_links = driver.find_elements(By.TAG_NAME, "a")
                                valid_links = [link for link in valid_links if link.is_displayed() and link.get_attribute("href")]
                    elif activity["action"] == "browse" and activity["terms"]:
                        search_id = "searchInput" if "wikipedia" in activity["url"].lower() else "search"
                        try:
                            search_box = driver.find_element(By.ID, search_id)
                            search_term = random.choice(activity["terms"])
                            for char in search_term:
                                search_box.send_keys(char)
                                time.sleep(random.uniform(0.05, 0.2))
                            search_box.send_keys(Keys.RETURN)
                            time.sleep(random.uniform(3, 7))
                            # Simulate clicking on internal links
                            links = driver.find_elements(By.TAG_NAME, "a")
                            valid_links = [link for link in links if link.is_displayed() and link.get_attribute("href") and activity["url"] in link.get_attribute("href")]
                            for _ in range(min(activity["clicks"], len(valid_links))):
                                if valid_links:
                                    link_to_click = random.choice(valid_links[:5])
                                    ActionChains(driver).move_to_element(link_to_click).click().perform()
                                    time.sleep(random.uniform(2, 5))
                                    driver.back()
                                    time.sleep(random.uniform(1, 3))
                                    links = driver.find_elements(By.TAG_NAME, "a")
                                    valid_links = [link for link in links if link.is_displayed() and link.get_attribute("href") and activity["url"] in link.get_attribute("href")]
                        except Exception as e:
                            self.logger.error(f"Error in browser browse action: {e}")
                    elif activity["action"] == "read":
                        # Simulate reading by scrolling through the page
                        if activity["scroll"]:
                            total_height = driver.execute_script("return document.body.scrollHeight")
                            scroll_distance = random.randint(200, 500)
                            current_pos = 0
                            for _ in range(random.randint(3, 8)):
                                current_pos += scroll_distance
                                if current_pos > total_height:
                                    break
                                driver.execute_script(f"window.scrollTo(0, {current_pos});")
                                time.sleep(random.uniform(1.5, 3.5))  # Mimic reading time
                            self.logger.info("Simulated reading by scrolling through page.")
                        # Click on a few articles if available
                        links = driver.find_elements(By.TAG_NAME, "a")
                        valid_links = [link for link in links if link.is_displayed() and link.get_attribute("href") and "article" in link.get_attribute("href").lower()]
                        for _ in range(min(activity["clicks"], len(valid_links))):
                            if valid_links:
                                link_to_click = random.choice(valid_links[:5])
                                ActionChains(driver).move_to_element(link_to_click).click().perform()
                                time.sleep(random.uniform(3, 7))
                                driver.back()
                                time.sleep(random.uniform(1, 3))
                                links = driver.find_elements(By.TAG_NAME, "a")
                                valid_links = [link for link in links if link.is_displayed() and link.get_attribute("href") and "article" in link.get_attribute("href").lower()]
                    
                    driver.quit()
                    self.logger.info("Browser simulation cycle completed.")
                    time.sleep(random.uniform(self.config['browser']['min_interval'], self.config['browser']['max_interval']))
                pause = random.uniform(5, 15)
                self.logger.info(f"Pausing for {pause:.2f} seconds before next cycle.")
                time.sleep(pause)
            except Exception as e:
                self.logger.error(f"Error in simulation: {e}")
                time.sleep(10)
