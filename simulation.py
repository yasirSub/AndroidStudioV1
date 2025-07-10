import time
import random
import pyautogui
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
                #if self.config['browser']['enabled']:
                #    # Browser simulation code is now disabled
                #    pass
                pause = random.uniform(5, 15)
                self.logger.info(f"Pausing for {pause:.2f} seconds before next cycle.")
                time.sleep(pause)
            except Exception as e:
                self.logger.error(f"Error in simulation: {e}")
                time.sleep(10)
