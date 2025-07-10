# Anoid

Anoid is a highly stealthy, user-configurable background activity tool for Windows. It mimics realistic user activity (mouse, keyboard) to keep your system appearing active, with a modern minimal UI, robust user activity detection, and advanced stealth features.

---

## Project Overview
- **Type:** Desktop Automation Utility
- **Platform:** Windows
- **Language:** Python 3.8+
- **UI:** Modern Tkinter
- **Installer:** Provided (see below)

---

## Features
- **Stealth & Minimalism:** Runs invisibly, only visible in the tray when minimized. All files and icons use generic names (anoid.json, anoid.log). UI is minimal and modern.
- **Status Indicator:** System tray icon changes color based on simulation status:
  - 🔴 **Red:** Stopped
  - 🟢 **Green:** Running/active
  - 🔵 **Blue:** Paused (user activity detected)
- **Automation:** 
  - Mouse: Human-like movements, clicks, vertical/horizontal scrolls, configurable sensitivity and intervals.
  - Keyboard: Realistic typing, random phrases, typos, and hotkeys. Includes a feature to type the contents of a .txt file after a delay (enable/disable in Keyboard tab).
- **Resource Usage:** See real-time CPU, RAM, and GPU usage in the UI and tray tooltip.
- **Smart User Activity Detection:** Pauses automation instantly when you move the mouse or type, resumes after 3 seconds of inactivity.
- **Tray Integration:** Minimizes to tray by default and after starting. Tray menu allows show, start, stop, and exit.
- **Configurable:** All features, intervals, and behaviors are user-configurable via the UI or `config/anoid.json`.
- **Robust Logging:** Logs to `config/anoid.log` with error handling.
- **Migration:** Old config/log files are auto-migrated to stealth names.

---

## Installation

1. **Download the Installer:**
   - [installer_output/AndroidStudioSetup.exe](https://github.com/yasirSub/AndroidStudioV1/releases)

2. **Run the Installer:**
   - Double-click `AndroidStudioSetup.exe` and follow the prompts.
   - The app will be installed to your Program Files by default.

3. **Launch the App:**
   - Use the Start Menu or desktop shortcut to launch.

4. **Manual (Developer) Install:**
   - Clone this repo and run:
     ```sh
     pip install -r requirements.txt
     python run_anoid.py
     ```

---

## Usage

### Graphical UI (Recommended)
1. Configure automation options in the minimal tabbed UI (Mouse, Keyboard, Advanced, Log).
2. Click "Start" to begin automation. The app will minimize to tray.
3. Use the tray icon to show, start, stop, or exit.
4. All changes are saved to `config/anoid.json`.
5. In the Keyboard tab, you can enable the "Type from text file" feature, select a file, set a delay, and start typing the file's contents automatically.
6. See live resource usage (CPU, RAM, GPU) in the Advanced tab and tray tooltip.

### Hotkeys
- **ALT+`**: Hide and show from tray

---

## Configuration
All settings are stored in `config/anoid.json`. Example:
```json
{
  "mouse": { "enabled": true, "movements": 5, ... },
  "keyboard": { "enabled": true, "actions": 3, ... },
  "ui": { "dark_mode": true, ... }
}
```
- **Mouse:** Movements, scrolls, sensitivity, intervals, horizontal scrolls.
- **Keyboard:** Phrases, actions, intervals, typos, Dart mode, type from file.
- **UI:** Dark mode, notifications, idle timeout, minimize on start, auto-start simulation.

---

## Resource Usage
- **Advanced tab:** Shows live CPU, RAM, and GPU usage.
- **Tray tooltip:** Hover over the tray icon to see resource usage.

---

## Directory Structure
```
project-root/
├── core/                # Main UI and tray logic
├── ui/                  # UI components
├── simulation/          # Simulation logic
├── logic/               # Config, uninstall, resource logic
├── config/              # User config and logs
├── run_anoid.py         # GUI entry point
├── main.py              # CLI entry point
├── requirements.txt     # Python dependencies
├── README.md            # This file
...
```

---

## Troubleshooting
- **Tray icon not visible or errors on Windows:** Try running as administrator, ensure `pystray` and `pillow` are installed, and that your system tray is not overloaded.
- **UI does not launch:** Ensure all dependencies are installed and run with Python 3.8+.
- **Resource usage not shown:** Ensure `psutil` and `GPUtil` are installed.
- **Large files warning:** If you see GitHub warnings about large files, consider using [Git LFS](https://git-lfs.github.com/).

---

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## Contact & Support
- **Author:** Yasir Subhani


---

## License
MIT
