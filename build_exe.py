import os
import subprocess
import sys

def build():
    print("Starting AndroidStudioV1 Build Process (V1.1 PRO)...")
    
    # Ensure pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Path to the main script
    main_script = "main.py"
    
    # Path to the logo
    logo_file = "Android_Studio_Logo_(2023).svg.png"
    
    # Build command
    # --noconsole: Hide terminal window (since it's a GUI/Tray app)
    # --onefile: Bundle into a single EXE
    # --add-data: Include the logo file
    # --icon: Set the EXE icon (if we had an .ico, but we can use the png for some aspects)
    # --name: Resulting EXE name
    
    cmd = [
        "pyinstaller",
        "--noconsole",
        "--onefile",
        f"--add-data={logo_file};.",
        f"--name=AndroidStudioV1",
        "--clean",
        main_script
    ]
    
    print(f"Executing: {' '.join(cmd)}")
    try:
        subprocess.check_call(cmd)
        print("\n" + "="*40)
        print("BUILD SUCCESSFUL!")
        print(f"Your standalone installer is located in: {os.path.join(os.getcwd(), 'dist', 'AndroidStudioV1.exe')}")
        print("="*40)
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed: {e}")

if __name__ == "__main__":
    build()
