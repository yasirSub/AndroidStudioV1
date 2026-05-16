import time
import random
import pyautogui
import logging
import threading
import os
import ctypes
from datetime import datetime
try:
    import pygetwindow as gw
except ImportError:
    gw = None

# Windows Constants for keeping screen on
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

class SimulationEngine:
    def __init__(self, config_manager, logger=None):
        self.config_manager = config_manager
        self.logger = logger or logging.getLogger("android_studio")
        self.running = False
        self.paused = False
        self.thread = None
        self.status_callback = None
        self.last_activity_time = 0
        self.mouse_activity_log = [] # List of (timestamp, x, y)
        self.keyboard_buffer = ""
        
        # Disable pyautogui fail-safe for background operation
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0  # Remove default delay for smoother custom movement
        
        self.ignoring_activity = False

    def set_status_callback(self, callback):
        """Set a callback for status changes (running, stopped, paused)"""
        self.status_callback = callback

    def _keep_screen_on(self, active=True):
        """Prevents the computer from sleeping or turning off the screen."""
        if os.name == 'nt': # Windows only
            try:
                if active:
                    ctypes.windll.kernel32.SetThreadExecutionState(
                        ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
                    )
                else:
                    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
            except Exception as e:
                self.logger.warning(f"Failed to set execution state: {e}")

    def _notify_status(self, status):
        if self.status_callback:
            self.status_callback(status)

    def start(self):
        if not self.running:
            self.running = True
            self.paused = False
            self._keep_screen_on(True) # Caffeine mode ON
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()
            self._start_activity_listener()
            self._notify_status("running")
            self.logger.info("Simulation engine started. Screen persistence active.")

    def stop(self):
        if self.running:
            self.running = False
            self._keep_screen_on(False) # Caffeine mode OFF
            self._stop_activity_listener()
            if self.thread:
                self.thread.join(timeout=1.0)
            self._notify_status("stopped")
            self.logger.info("Simulation engine stopped.")

    def _start_activity_listener(self):
        try:
            from pynput import mouse, keyboard
            self._stop_activity_listener()
            
            def on_activity(*args, **kwargs):
                if not self.running or self.ignoring_activity:
                    return

                self.last_activity_time = time.time()
                
                # Check if it's a mouse move event (args will have x, y)
                is_mouse_move = len(args) >= 2 and isinstance(args[0], (int, float))
                
                if is_mouse_move:
                    # Implement "move mouse in speed" requirement
                    now = time.time()
                    x, y = args[0], args[1]
                    self.mouse_activity_log.append((now, x, y))
                    
                    # Keep only last 2 seconds of history
                    self.mouse_activity_log = [entry for entry in self.mouse_activity_log if now - entry[0] <= 2.0]
                    
                    if len(self.mouse_activity_log) > 5:
                        # Calculate total distance moved in last 2 seconds
                        total_dist = 0
                        for i in range(1, len(self.mouse_activity_log)):
                            p1 = self.mouse_activity_log[i-1]
                            p2 = self.mouse_activity_log[i]
                            dist = ((p2[1]-p1[1])**2 + (p2[2]-p1[2])**2)**0.5
                            total_dist += dist
                        
                        # If distance moved in 2s is significant (e.g. 500 pixels)
                        # adjust threshold based on screen size or user preference
                        if total_dist > 800:
                            if not self.paused:
                                self.logger.info(f"Rapid mouse activity detected ({int(total_dist)}px in 2s). Pausing.")
                                self.toggle_pause()
                                threading.Timer(3.5, self._check_resume).start()
                    return
                
                # For keyboard, check for "s" or "start" + Enter to resume
                try:
                    from pynput import keyboard
                    if isinstance(args[0], keyboard.KeyCode) and args[0].char:
                        self.keyboard_buffer += args[0].char.lower()
                        # Keep buffer short
                        if len(self.keyboard_buffer) > 10:
                            self.keyboard_buffer = self.keyboard_buffer[-10:]
                    elif args[0] == keyboard.Key.enter:
                        if self.keyboard_buffer in ["s", "start"]:
                            if self.paused:
                                self.logger.info(f"Magic command '{self.keyboard_buffer}' detected. Resuming immediately.")
                                self.toggle_pause()
                                self.keyboard_buffer = ""
                                return # Important: don't let the "User interaction" block below pause it again!
                        self.keyboard_buffer = ""
                    else:
                        # Other special keys clear the buffer
                        self.keyboard_buffer = ""
                except Exception:
                    self.keyboard_buffer = ""

                # For any keypress (including the ones for start), we still record activity
                # and pause if not already paused (unless it's the resume command)
                if not self.paused:
                    self.logger.info("User interaction detected. Pausing simulation.")
                    self.toggle_pause()
                    threading.Timer(3.5, self._check_resume).start()
            
            self.activity_listener = {
                'mouse': mouse.Listener(on_move=on_activity, on_click=on_activity, on_scroll=on_activity),
                'keyboard': keyboard.Listener(on_press=on_activity)
            }
            self.activity_listener['mouse'].start()
            self.activity_listener['keyboard'].start()
        except ImportError:
            self.logger.warning("pynput not installed. Activity detection disabled.")

    def _stop_activity_listener(self):
        if hasattr(self, 'activity_listener') and self.activity_listener:
            for l in self.activity_listener.values():
                try: l.stop()
                except: pass
            self.activity_listener = None

    def _check_resume(self):
        if self.running and self.paused:
            # Only resume if at least 3 seconds have passed since the LAST activity
            elapsed = time.time() - self.last_activity_time
            if elapsed >= 3.0:
                self.logger.info(f"Inactivity detected for {elapsed:.1f}s. Resuming simulation...")
                self.toggle_pause()
            else:
                # Still active recently, schedule another check in a second
                threading.Timer(1.0, self._check_resume).start()

    def toggle_pause(self):
        self.paused = not self.paused
        status = "paused" if self.paused else "running"
        self._notify_status(status)
        self.logger.info(f"Simulation engine {status}.")

    def _is_within_schedule(self, schedule_config):
        """Checks if the current time is within the allowed work schedule."""
        if not schedule_config.get('enabled', False):
            return True
            
        now = datetime.now()
        
        # Check days
        day_map = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6}
        allowed_days_str = schedule_config.get('days', 'Mon,Tue,Wed,Thu,Fri').lower()
        allowed_days = [day_map.get(d.strip()[:3]) for d in allowed_days_str.split(',') if d.strip()[:3] in day_map]
        
        if now.weekday() not in allowed_days:
            return False
            
        # Check time
        try:
            start_time = datetime.strptime(schedule_config.get('start_time', '09:00'), '%H:%M').time()
            end_time = datetime.strptime(schedule_config.get('end_time', '17:00'), '%H:%M').time()
            current_time = now.time()
            
            if start_time < end_time:
                return start_time <= current_time <= end_time
            else: # Overnight schedule (e.g. 22:00 to 06:00)
                return current_time >= start_time or current_time <= end_time
        except Exception as e:
            self.logger.error(f"Schedule time parsing error: {e}")
            return True # Default to True on error to avoid locking the app

    def _run_loop(self):
        while self.running:
            if self.paused:
                self._keep_screen_on(False) # Save battery while paused
                time.sleep(1)
                continue
            
            try:
                config = self.config_manager.get_config()
                
                # Check Work Schedule
                if not self._is_within_schedule(config.get('schedule', {})):
                    self.logger.info("Outside work schedule. Pausing activity.")
                    self._keep_screen_on(False)
                    time.sleep(60) # Check again in a minute
                    continue
                
                # Dynamic optimization: Check battery status
                battery_saving = False
                try:
                    import psutil
                    battery = psutil.sensors_battery()
                    if battery and not battery.power_plugged:
                        battery_saving = True
                        self.logger.info("Battery mode detected. Scaling back activity to save power.")
                except Exception:
                    pass

                # Ensure editor is focused - Optimized: don't scan windows every single loop
                # only if we need to or periodically
                if not hasattr(self, '_last_focus_check') or time.time() - self._last_focus_check > 30:
                    self._ensure_editor_focus()
                    
                    # Clean processes if enabled
                    if config.get('ui', {}).get('process_cleaner_enabled', False):
                        self._clean_processes()
                        
                    self._last_focus_check = time.time()
                
                # Mouse Simulation
                if config.get('mouse', {}).get('enabled', False):
                    self._simulate_mouse(config['mouse'])
                
                # Keyboard Simulation
                if config.get('keyboard', {}).get('enabled', False):
                    self._simulate_keyboard(config['keyboard'])
                
                # Random pause between cycles - Optimized for "Unlimited" feel
                # Reduced significantly to keep activity continuous as requested
                base_pause = 2 if not battery_saving else 10
                max_pause = 8 if not battery_saving else 30
                pause_time = random.uniform(base_pause, max_pause)
                
                self.logger.info(f"Cycle completed. Resuming in {pause_time:.1f}s...")
                
                # Interruptible sleep
                for _ in range(int(pause_time)):
                    if not self.running or self.paused: break
                    time.sleep(1)
                time.sleep(pause_time % 1)
                
            except Exception as e:
                self.logger.error(f"Error in simulation loop: {e}")
                time.sleep(5)

    def _human_mouse_move(self, end_x, end_y, duration=1.0):
        """Moves the mouse in a more human-like curved path."""
        start_x, start_y = pyautogui.position()
        
        # Ensure we don't trigger the pause while moving
        self.ignoring_activity = True
        
        try:
            # Create control points for a Bezier curve
            # We'll use 2 control points for a cubic Bezier
            # Add more randomness to control points for less "robotic" look
            dist = ((end_x - start_x)**2 + (end_y - start_y)**2)**0.5
            jitter = dist * 0.2 # 20% jitter based on distance
            
            cp1_x = start_x + (end_x - start_x) * random.uniform(0.1, 0.4) + random.randint(-int(jitter), int(jitter))
            cp1_y = start_y + (end_y - start_y) * random.uniform(0.1, 0.4) + random.randint(-int(jitter), int(jitter))
            
            cp2_x = start_x + (end_x - start_x) * random.uniform(0.6, 0.9) + random.randint(-int(jitter), int(jitter))
            cp2_y = start_y + (end_y - start_y) * random.uniform(0.6, 0.9) + random.randint(-int(jitter), int(jitter))
            
            steps = int(duration * 60) # 60 steps per second for smoothness
            if steps < 10: steps = 10
            
            for i in range(steps + 1):
                if not self.running or self.paused: break
                t = i / steps
                
                # Cubic Bezier formula
                x = (1-t)**3 * start_x + 3*(1-t)**2*t * cp1_x + 3*(1-t)*t**2 * cp2_x + t**3 * end_x
                y = (1-t)**3 * start_y + 3*(1-t)**2*t * cp1_y + 3*(1-t)*t**2 * cp2_y + t**3 * end_y
                
                pyautogui.moveTo(int(x), int(y))
                # Small variable sleep to simulate non-constant speed
                # Humans don't move at a perfectly constant velocity
                time.sleep((duration / steps) * random.uniform(0.7, 1.3))
        finally:
            self.ignoring_activity = False

    def _simulate_mouse(self, mouse_config):
        self.ignoring_activity = True
        try:
            self._do_simulate_mouse(mouse_config)
        finally:
            self.ignoring_activity = False

    def _do_simulate_mouse(self, mouse_config):
        screen_width, screen_height = pyautogui.size()
        movements = mouse_config.get('movements', 10) # Increased from 5 to 10
        
        for _ in range(movements):
            if not self.running or self.paused: break
            
            # Natural movement
            end_x = random.randint(int(screen_width * 0.1), int(screen_width * 0.9))
            end_y = random.randint(int(screen_height * 0.1), int(screen_height * 0.9))
            
            duration = random.uniform(mouse_config.get('min_duration', 0.5), mouse_config.get('max_duration', 2.0))
            
            # Use human-like movement
            self._human_mouse_move(end_x, end_y, duration)
            
            # Occasional interaction
            action_chance = random.random()
            if action_chance < 0.2:
                self.ignoring_activity = True
                pyautogui.click()
                self.ignoring_activity = False
            elif action_chance < 0.25:
                self.ignoring_activity = True
                pyautogui.rightClick()
                self.ignoring_activity = False
            elif action_chance < 0.3:
                # Scroll activity
                self.ignoring_activity = True
                try:
                    scroll_amount = random.randint(-5, 5) * mouse_config.get('scroll_sensitivity', 3)
                    pyautogui.scroll(scroll_amount)
                finally:
                    self.ignoring_activity = False
            
            # Small interval between movements
            time.sleep(random.uniform(mouse_config.get('min_interval', 1.0), mouse_config.get('max_interval', 3.0)))

    def _human_type(self, text, base_interval=0.2):
        """Types text with random intervals and occasional mistakes. Default slowed down as requested."""
        for char in text:
            if not self.running or self.paused: break
            
            # 2% chance of a typo
            if random.random() < 0.02 and len(char.strip()) > 0:
                # Type a random neighboring key (simulated)
                self.ignoring_activity = True
                try:
                    pyautogui.write(random.choice("asdfghjkl"), interval=base_interval)
                    time.sleep(random.uniform(0.1, 0.3))
                    pyautogui.press('backspace')
                    time.sleep(random.uniform(0.3, 0.5)) # Increased delay for stability
                finally:
                    self.ignoring_activity = False
            
            self.ignoring_activity = True
            try:
                pyautogui.write(char, interval=base_interval * random.uniform(0.5, 1.5))
                
                # Slightly longer pause after punctuation
                if char in ".,!?;":
                    time.sleep(random.uniform(0.2, 0.5))
            finally:
                self.ignoring_activity = False

    def _simulate_keyboard(self, kb_config):
        dart_enabled = kb_config.get('dart_enabled', False)
        # Slowed down interval (0.1 for dart, 0.2 for text)
        base_interval = 0.12 if dart_enabled else 0.25
        
        # Small delay to ensure focus is solid before typing
        time.sleep(0.5)
        
        self.ignoring_activity = True
        try:
            self._do_simulate_keyboard(kb_config, dart_enabled, base_interval)
        finally:
            self.ignoring_activity = False

    def _do_simulate_keyboard(self, kb_config, dart_enabled, base_interval):
        actions = kb_config.get('actions', 10) # Increased from 3 to 10 for more continuous typing
        if dart_enabled:
            dart_snippets = [
                "void main() {\n  runApp(const MyApp());\n}",
                "class MyApp extends StatelessWidget {\n  @override\n  Widget build(BuildContext context) {\n    return MaterialApp(\n      title: 'Flutter Demo',\n      theme: ThemeData(primarySwatch: Colors.blue),\n      home: const MyHomePage(title: 'Flutter Home Page'),\n    );\n  }\n}",
                "Future<void> _incrementCounter() async {\n  setState(() {\n    _counter++;\n  });\n  await Future.delayed(const Duration(milliseconds: 500));\n  debugPrint('Counter incremented to $_counter');\n}",
                "ListView.builder(\n  itemCount: items.length,\n  itemBuilder: (context, index) {\n    return ListTile(\n      title: Text('Item $index'),\n      onTap: () => print('Tapped $index'),\n    );\n  },\n)",
                "class UserProfile extends StatefulWidget {\n  final String userId;\n  const UserProfile({Key? key, required this.userId}) : super(key: key);\n  @override\n  _UserProfileState createState() => _UserProfileState();\n}",
                "final response = await http.get(Uri.parse('https://api.example.com/data'));\nif (response.statusCode == 200) {\n  final data = jsonDecode(response.body);\n  return DataModel.fromJson(data);\n} else {\n  throw Exception('Failed to load data');\n}",
                "class DataModel {\n  final int id;\n  final String name;\n  DataModel({required this.id, required this.name});\n  factory DataModel.fromJson(Map<String, dynamic> json) {\n    return DataModel(\n      id: json['id'] as int,\n      name: json['name'] as String,\n    );\n  }\n}",
                "class AnimationWidget extends StatefulWidget {\n  @override\n  _AnimationWidgetState createState() => _AnimationWidgetState();\n}\nclass _AnimationWidgetState extends State<AnimationWidget> with SingleTickerProviderStateMixin {\n  late AnimationController _controller;\n  @override\n  void initState() {\n    _controller = AnimationController(duration: const Duration(seconds: 2), vsync: this)..repeat();\n    super.initState();\n  }\n  @override\n  void dispose() {\n    _controller.dispose();\n    super.dispose();\n  }\n}",
                "Widget _buildDeepNestedUI() {\n  return Container(\n    decoration: BoxDecoration(\n      gradient: LinearGradient(colors: [Colors.blue, Colors.purple]),\n    ),\n    child: Center(\n      child: Card(\n        elevation: 10,\n        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),\n        child: Padding(\n          padding: const EdgeInsets.all(32.0),\n          child: Column(\n            mainAxisSize: MainAxisSize.min,\n            children: [\n              Icon(Icons.rocket_launch, size: 64, color: Colors.blue),\n              SizedBox(height: 16),\n              Text('Advanced UI Architecture', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),\n              Text('Implementing complex design patterns...'),\n            ],\n          ),\n        ),\n      ),\n    ),\n  );\n}",
                "abstract class BaseRepository<T> {\n  Future<List<T>> getAll();\n  Future<T> getById(String id);\n  Future<void> save(T item);\n}\nclass UserRepository extends BaseRepository<User> {\n  @override\n  Future<List<User>> getAll() async {\n    final db = await DatabaseHelper.instance.database;\n    final maps = await db.query('users');\n    return List.generate(maps.length, (i) => User.fromMap(maps[i]));\n  }\n}"
            ]
            for _ in range(actions):
                if not self.running or self.paused: break
                snippet = random.choice(dart_snippets)
                for line in snippet.split('\n'):
                    # Strip leading whitespace and type - let the editor auto-indent
                    self._human_type(line.lstrip(), base_interval)
                    self.ignoring_activity = True
                    pyautogui.press('enter')
                    self.ignoring_activity = False
                time.sleep(random.uniform(2, 5))
        else:
            phrases = kb_config.get('phrases', ['coding...', 'android studio', 'debugging'])
            for _ in range(actions):
                if not self.running or self.paused: break
                phrase = random.choice(phrases)
                self._human_type(phrase, base_interval)
                self.ignoring_activity = True
                pyautogui.press('enter')
                self.ignoring_activity = False
                time.sleep(random.uniform(kb_config.get('min_interval', 2.0), kb_config.get('max_interval', 5.0)))

    def _dismiss_notifications(self):
        """Attempts to dismiss Windows toast notifications if they appear."""
        if not gw: return
        try:
            # Common titles/classes for Windows notifications
            toast_titles = ["Notification", "New notification", "Action Center"]
            for title in toast_titles:
                toasts = gw.getWindowsWithTitle(title)
                for toast in toasts:
                    # Don't close the main editor! 
                    if "Visual Studio" not in toast.title and "Android Studio" not in toast.title:
                        toast.close()
        except Exception:
            pass

    def _clean_processes(self):
        """Identifies and terminates unnecessary background processes to save resources and maintain a work profile."""
        try:
            import psutil
            # Define keywords for 'unnecessary' or 'distracting' processes
            distracting_apps = [
                "steam", "epicgames", "discord", "spotify", "netflix", 
                "battle.net", "origin", "uplay", "vlc", "mpc-hc",
                "utorrent", "bittorrent", "qbittorrent"
            ]
            
            # Whitelist of things we MUST NOT kill
            essential_keywords = ["antigravity", "cursor", "visual studio", "android studio", "python", "anoid", "code"]
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    name = proc.info['name'].lower()
                    
                    # Skip essential processes
                    if any(essential in name for essential in essential_keywords):
                        continue
                        
                    # Check if it's a known distracting app
                    is_distracting = any(distract in name for distract in distracting_apps)
                    
                    # Or if it's using too much CPU and isn't a known system process
                    high_cpu = proc.info['cpu_percent'] > 30.0 # Using more than 30% CPU
                    
                    if is_distracting or high_cpu:
                        # Double check it's not a critical system process (rough check)
                        system_paths = ["c:\\windows\\system32", "c:\\windows\\syswow64"]
                        try:
                            exe_path = proc.exe().lower()
                            if any(path in exe_path for path in system_paths):
                                continue
                        except:
                            pass
                            
                        self.logger.info(f"Terminating unnecessary process: {proc.info['name']} (PID: {proc.info['pid']})")
                        proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            self.logger.error(f"Process cleaning error: {e}")

    def _ensure_editor_focus(self):
        """Maintains a focused coding environment by minimizing other apps and launching VS Code if needed."""
        self._dismiss_notifications()
        if not gw: return
        
        target_titles = ["Visual Studio Code", "Android Studio", "Cursor", "IntelliJ", "Sublime", "Notepad++", "Notepad", "EditPlus", "UltraEdit", "test", "Antigravity"]
        editor_found = False
        
        try:
            all_windows = gw.getAllWindows()
            for window in all_windows:
                # Skip empty titles or system windows
                if not window.title or window.title in ["", "Program Manager", "Taskbar"]:
                    continue
                
                is_editor = any(target.lower() in window.title.lower() for target in target_titles)
                
                # Whitelist development and workspace tools
                workspace_tools = ["Antigravity", "Terminal", "PowerShell", "Command Prompt", "Git", "GitHub Desktop"]
                is_workspace_tool = any(tool.lower() in window.title.lower() for tool in workspace_tools)
                
                if is_editor or is_workspace_tool:
                    if not editor_found and is_editor:
                        # Found our primary editor, make sure it's visible and active
                        if window.isMinimized:
                            window.restore()
                        if not window.isActive:
                            window.activate()
                        
                        # Added click to ensure cursor is active in the editor
                        self.ignoring_activity = True
                        try:
                            # Click slightly below top-left to avoid menus but hit editor area
                            # Or just center click if it's the first focus
                            if not hasattr(self, '_first_focus_click') or time.time() - self._first_focus_click > 300:
                                pyautogui.click(window.left + 200, window.top + 200)
                                self._first_focus_click = time.time()
                        finally:
                            self.ignoring_activity = False
                            
                        editor_found = True
                else:
                    # Not an editor - CLOSE it only if explicitly enabled in config
                    config = self.config_manager.get_config()
                    if config.get('ui', {}).get('close_non_editors', False):
                        system_windows = ["Taskbar", "Program Manager", "Start", "Windows Search", "Android Studio", "Anoid", "Antigravity"]
                        if not any(sw.lower() in window.title.lower() for sw in system_windows):
                            try:
                                self.logger.info(f"Closing non-editor application: {window.title}")
                                window.close()
                            except:
                                try: window.minimize()
                                except: pass

            # If no editor was found at all, log a warning and return False
            if not editor_found:
                self.logger.warning("No active editor found (VS Code, Android Studio, etc.). Simulation may type into the wrong window.")
                return False
            
            return editor_found
        except Exception as e:
            self.logger.debug(f"Focus management error: {e}")
            return False
