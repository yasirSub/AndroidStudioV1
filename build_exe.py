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
    logo_dir = "assets"
    
    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        f"--add-data={logo_dir};assets",
        f"--icon=assets/logo.ico",
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
