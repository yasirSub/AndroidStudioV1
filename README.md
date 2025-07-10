# Anoid

Anoid is a highly stealthy, user-configurable background activity simulator for Windows. It mimics realistic user activity (mouse, keyboard, browser) to keep your system appearing active, with a modern minimal UI, robust user activity detection, and advanced stealth features.

## Features

- **Stealth & Minimalism**: Runs invisibly, only visible in the tray when minimized. All files and icons use generic names (anoid.json, anoid.log). UI is minimal and modern.
- **Status Indicator**: System tray icon changes color based on simulation status:
  - 🔴 **Red**: Simulation stopped
  - 🟢 **Green**: Simulation running/active
  - 🔵 **Blue**: Simulation paused (user activity detected)
- **Simulation**: 
  - Mouse: Human-like movements, clicks, vertical/horizontal scrolls, configurable sensitivity and intervals.
  - Keyboard: Realistic typing, random phrases, typos, and hotkeys.
  - Browser: Headless Chrome activity, random searches, and browsing.
- **Smart User Activity Detection**: Pauses simulation instantly when you move the mouse or type, resumes after 3 seconds of inactivity.
- **Tray Integration**: Minimizes to tray by default and after starting. Tray menu allows show, start, stop, and exit.
- **Configurable**: All features, intervals, and behaviors are user-configurable via the UI or `config/anoid.json`.
- **Global Hotkey**: (Ctrl+Shift+P) to pause/resume simulation (if enabled).
- **Robust Logging**: Logs to `config/anoid.log` with error handling.
- **Migration**: Old config/log files are auto-migrated to stealth names.

## Installation

1. **Requirements:**
   - Python 3.8+
   - Google Chrome (for browser simulation)
   - [ChromeDriver](https://chromedriver.chromium.org/downloads) matching your Chrome version (place in PATH or project root)

2. **Install dependencies:**
   ```
   pip install pyautogui selenium pynput pystray pillow keyboard
   ```
   (You may also need `pip install tk` if not present.)

3. **Clone or extract the Anoid project.**

## Usage

### Graphical UI (Recommended)

1. Run:
   ```
   python run_anoid.py
   ```
2. Configure simulation options in the minimal tabbed UI (Mouse, Keyboard, Browser, UI settings).
3. Click "Start" to begin simulation. The app will minimize to tray.
4. Use the tray icon to show, start, stop, or exit.
5. All changes are saved to `config/anoid.json`.

### Direct Simulation (Headless/CLI)

- Run:
  ```
  python main.py
  ```
- Simulation runs based on `config/anoid.json`. Stop with `Esc`.

## Configuration

All settings are stored in `config/anoid.json`. Example:
```json
{
  "mouse": { "enabled": true, "movements": 5, ... },
  "keyboard": { "enabled": true, "actions": 3, ... },
  "browser": { "enabled": true, "headless": true, ... },
  "ui": { "dark_mode": true, "hotkey_control": false, ... }
}
```
- **Mouse**: Movements, scrolls, sensitivity, intervals, horizontal scrolls.
- **Keyboard**: Phrases, actions, intervals, typos, Dart mode.
- **Browser**: Headless, intervals, random user-agent.
- **UI**: Dark mode, hotkey, notifications, idle timeout, minimize on start.

## Stealth & Security
- All app, config, and log files use generic names (anoid).
- Tray icon is a generic blue square.
- No notifications or hotkeys are enabled by default.
- Simulation never runs while you are active (mouse/keyboard detection).

## Troubleshooting
- **Tray icon not visible or errors on Windows**: Try running as administrator, ensure `pystray` and `pillow` are installed, and that your system tray is not overloaded.
- **Browser simulation fails**: Ensure Chrome and ChromeDriver are installed and compatible.
- **UI does not launch**: Ensure all dependencies are installed and run with Python 3.8+.

## Disclaimer
This tool is for educational and testing purposes only. Use responsibly and in accordance with your local laws and workplace policies. The developers are not responsible for misuse.

## License
MIT
