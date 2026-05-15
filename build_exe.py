import os
import subprocess
import sys

def build():
    print("Starting Anoid EXE Build Process...")
    
    # 1. Install requirements
    print("Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    # 2. Define the command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--noconsole",
        "--clean",
        "--name=Anoid",
        "--add-data=config;config",
        "--add-data=requirements.txt;.",
        "main.py"
    ]

    print(f"Running PyInstaller: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("\nBuild Successful!")
        print(f"Your EXE is located in: {os.path.join(os.getcwd(), 'dist', 'Anoid.exe')}")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild Failed with error: {e}")

if __name__ == "__main__":
    build()
