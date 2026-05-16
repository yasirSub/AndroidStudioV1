from setuptools import setup, find_packages

setup(
    name="AndroidStudioV1",
    version="1.1.0",
    packages=find_packages(),
    install_requires=[
        "pyautogui",
        "pynput",
        "psutil",
        "pygetwindow",
        "Pillow",
        "pystray",
        "keyboard"
    ],
    entry_points={
        "console_scripts": [
            "androidstudiov1=main:main",
        ],
    },
    author="AndroidStudioV1 Team",
    description="A professional background simulation utility for Android Studio developers.",
    keywords="automation, simulation, android studio, productivity",
    url="https://github.com/AndroidStudioV1/AndroidStudioV1",
)
