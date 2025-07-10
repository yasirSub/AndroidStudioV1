import os
import subprocess

def run_uninstaller():
    """Attempt to run the uninstaller or open Windows Apps & Features as fallback."""
    possible_paths = [
        os.path.expandvars(r"%ProgramFiles%/AndroidStudioV1/Uninstall.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%/AndroidStudioV1/Uninstall.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%/Programs/AndroidStudioV1/Uninstall.exe"),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            subprocess.Popen([path])
            return True
    # Fallback: open Windows Apps & Features
    subprocess.Popen("start ms-settings:appsfeatures", shell=True)
    return False
