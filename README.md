# Anoid

Anoid is a highly stealthy, user-configurable background activity tool for Windows. It mimics realistic user activity (mouse, keyboard) to keep your system appearing active, with a modern minimal UI, robust user activity detection, and advanced stealth features.

## Features

- **Stealth & Minimalism**: Runs invisibly, only visible in the tray when minimized. All files and icons use generic names (anoid.json, anoid.log). UI is minimal and modern.
- **Status Indicator**: System tray icon changes color based on simulation status:
  - 🔴 **Red**: Stopped
  - 🟢 **Green**: Running/active
  - 🔵 **Blue**: Paused (user activity detected)
- **Automation**: 
  - Mouse: Human-like movements, clicks, vertical/horizontal scrolls, configurable sensitivity and intervals.
  - Keyboard: Realistic typing, random phrases, typos, and hotkeys. Includes a feature to type the contents of a .txt file after a delay (enable/disable in Keyboard tab).
- **Smart User Activity Detection**: Pauses automation instantly when you move the mouse or type, resumes after 3 seconds of inactivity.
- **Tray Integration**: Minimizes to tray by default and after starting. Tray menu allows show, start, stop, and exit.
- **Configurable**: All features, intervals, and behaviors are user-configurable via the UI or `config/anoid.json`.
- **Robust Logging**: Logs to `config/anoid.log` with error handling.
- **Migration**: Old config/log files are auto-migrated to stealth names.

## Installation (Release v1.0.1)

1. **Download the Installer:**
   - [installer_output/AndroidStudioSetup.exe](installer_output/AndroidStudioSetup.exe)

2. **Run the Installer:**
   - Double-click `AndroidStudioSetup.exe` and follow the prompts.
   - The app will be installed to your Program Files by default.

3. **Launch the App:**
   - Use the Start Menu or desktop shortcut to launch.

## Usage

### Graphical UI (Recommended)

1. Configure automation options in the minimal tabbed UI (Mouse, Keyboard, UI settings).
2. Click "Start" to begin automation. The app will minimize to tray.
3. Use the tray icon to show, start, stop, or exit.
4. All changes are saved to `config/anoid.json`.
5. In the Keyboard tab, you can enable the "Type from text file" feature, select a file, set a delay, and start typing the file's contents automatically.

- ALT+`: Hide and show from tray

## Configuration

All settings are stored in `config/anoid.json`. Example:
```json
{
  "mouse": { "enabled": true, "movements": 5, ... },
  "keyboard": { "enabled": true, "actions": 3, ... },
  "ui": { "dark_mode": true, ... }
}
```
- **Mouse**: Movements, scrolls, sensitivity, intervals, horizontal scrolls.
- **Keyboard**: Phrases, actions, intervals, typos, Dart mode, type from file.
- **UI**: Dark mode, notifications, idle timeout, minimize on start.

## Stealth & Security
- All app, config, and log files use generic names (anoid).
- Tray icon is a generic blue square.
- No notifications or hotkeys are enabled by default.
- Automation never runs while you are active (mouse/keyboard detection).

## Troubleshooting
- **Tray icon not visible or errors on Windows**: Try running as administrator, ensure `pystray` and `pillow` are installed, and that your system tray is not overloaded.
- **UI does not launch**: Ensure all dependencies are installed and run with Python 3.8+.

## Disclaimer
This tool is for educational and testing purposes only. Use responsibly and in accordance with your local laws and workplace policies. The developers are not responsible for misuse.

## License
MIT
