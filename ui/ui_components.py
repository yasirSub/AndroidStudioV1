import tkinter as tk
from tkinter import ttk
import os

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.id = None
        self.x = self.y = 0
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font="Tahoma 8 normal")
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

class UIComponents:
    def __init__(self, app):
        self.app = app
        self.root = app.root
        self.is_dark_mode = self.app.config.get('ui', {}).get('dark_mode', False)
        # UI variables (unchanged)
        self.mouse_enabled = tk.BooleanVar(value=self.app.config.get('mouse', {}).get('enabled', False))
        self.mouse_movements = tk.IntVar(value=self.app.config.get('mouse', {}).get('movements', 5))
        self.mouse_min_duration = tk.DoubleVar(value=self.app.config.get('mouse', {}).get('min_duration', 0.5))
        self.mouse_max_duration = tk.DoubleVar(value=self.app.config.get('mouse', {}).get('max_duration', 2.0))
        self.mouse_min_interval = tk.DoubleVar(value=self.app.config.get('mouse', {}).get('min_interval', 1.0))
        self.mouse_max_interval = tk.DoubleVar(value=self.app.config.get('mouse', {}).get('max_interval', 5.0))
        self.mouse_scrolls = tk.IntVar(value=self.app.config.get('mouse', {}).get('scrolls', 3))
        self.mouse_scroll_sensitivity = tk.IntVar(value=self.app.config.get('mouse', {}).get('scroll_sensitivity', 3))
        self.mouse_hscrolls = tk.IntVar(value=self.app.config.get('mouse', {}).get('hscrolls', 1))
        self.mouse_scroll_min_interval = tk.DoubleVar(value=self.app.config.get('mouse', {}).get('scroll_min_interval', 0.2))
        self.mouse_scroll_max_interval = tk.DoubleVar(value=self.app.config.get('mouse', {}).get('scroll_max_interval', 1.0))
        self.keyboard_enabled = tk.BooleanVar(value=self.app.config.get('keyboard', {}).get('enabled', False))
        self.keyboard_actions = tk.IntVar(value=self.app.config.get('keyboard', {}).get('actions', 3))
        self.keyboard_phrases = tk.StringVar(value=", ".join(self.app.config.get('keyboard', {}).get('phrases', ["hello"])))
        self.keyboard_min_interval = tk.DoubleVar(value=self.app.config.get('keyboard', {}).get('min_interval', 2.0))
        self.keyboard_max_interval = tk.DoubleVar(value=self.app.config.get('keyboard', {}).get('max_interval', 10.0))
        self.dart_enabled = tk.BooleanVar(value=self.app.config.get('keyboard', {}).get('dart_enabled', False))
        self.dart_lines = tk.IntVar(value=self.app.config.get('keyboard', {}).get('dart_lines', 10))
        self.code_writing_enabled = tk.BooleanVar(value=self.app.config.get('keyboard', {}).get('code_writing_enabled', True))
        self.browser_enabled = tk.BooleanVar(value=self.app.config.get('browser', {}).get('enabled', False))
        self.browser_headless = tk.BooleanVar(value=self.app.config.get('browser', {}).get('headless', True))
        self.browser_min_interval = tk.DoubleVar(value=self.app.config.get('browser', {}).get('min_interval', 10.0))
        self.browser_max_interval = tk.DoubleVar(value=self.app.config.get('browser', {}).get('max_interval', 30.0))
        self.auto_restart_var = tk.BooleanVar(value=self.app.auto_restart_enabled)
        self.idle_timeout_var = tk.IntVar(value=self.app.idle_timeout_minutes)
        self.hotkey_control_var = tk.BooleanVar(value=self.app.config.get('ui', {}).get('hotkey_control', True))
        self.notifications_enabled = tk.BooleanVar(value=self.app.config.get('ui', {}).get('notifications_enabled', False))
        self.minimize_on_start_var = tk.BooleanVar(value=self.app.config.get('ui', {}).get('minimize_on_start', True))
        self.log_text = None
        self.status_label = None
        self.glassy_bg_light = "#F5F5F7"  # Apple-like light background
        self.glassy_bg_dark = "#1E1E22"  # Apple-like dark background
        self.glassy_accent_light = "#007AFF"  # Apple blue accent
        self.glassy_accent_dark = "#0A84FF"  # Apple blue accent for dark mode

    def setup_ui(self):
        # --- Top Status & Controls Bar ---
        top = ttk.Frame(self.root)
        top.pack(fill='x', pady=(10, 10))
        # Status indicator
        self.status_label = tk.Label(top, text="Status: Stopped", font="Helvetica 12 bold", fg="#fff", bg="#d9534f", width=18)
        self.status_label.pack(side=tk.LEFT, padx=(15, 10), pady=5)
        # Start, Pause, Stop buttons
        start_btn = ttk.Button(top, text="▶ Start", command=self.app.start_simulation)
        start_btn.pack(side=tk.LEFT, padx=5)
        pause_btn = ttk.Button(top, text="⏸ Pause", command=lambda: self.app.simulation_controls.handle_user_activity())
        pause_btn.pack(side=tk.LEFT, padx=5)
        stop_btn = ttk.Button(top, text="■ Stop", command=self.app.stop_simulation)
        stop_btn.pack(side=tk.LEFT, padx=5)
        # Dark mode toggle
        dark_toggle_btn = ttk.Button(top, text="🌙" if not self.is_dark_mode else "☀️", width=3, command=self.toggle_dark_mode)
        dark_toggle_btn.pack(side=tk.RIGHT, padx=(0,15))
        Tooltip(dark_toggle_btn, "Toggle dark/light mode.")

        # --- Tabbed Settings Area ---
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=15, pady=10)

        # Mouse Tab
        mouse_tab = ttk.Frame(notebook)
        notebook.add(mouse_tab, text="🖱️ Mouse")
        tk.Label(mouse_tab, text="Mouse Activity", font="Helvetica 11 bold", pady=6).pack(anchor='w', padx=10, pady=(10,0))
        mouse_toggle = ttk.Checkbutton(mouse_tab, text="Enable Mouse Simulation", variable=self.mouse_enabled)
        mouse_toggle.pack(anchor='w', padx=20, pady=2)
        row = ttk.Frame(mouse_tab)
        row.pack(fill='x', pady=3, padx=10)
        ttk.Label(row, text="Movements:").pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.mouse_movements, width=5).pack(side=tk.LEFT, padx=3)
        ttk.Label(row, text="Scrolls:").pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.mouse_scrolls, width=4).pack(side=tk.LEFT, padx=3)
        ttk.Label(row, text="Scroll Sensitivity:").pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.mouse_scroll_sensitivity, width=4).pack(side=tk.LEFT, padx=3)
        ttk.Label(row, text="H-Scrolls:").pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.mouse_hscrolls, width=4).pack(side=tk.LEFT, padx=3)
        # Scroll interval row
        scroll_row = ttk.Frame(mouse_tab)
        scroll_row.pack(fill='x', pady=3, padx=10)
        ttk.Label(scroll_row, text="Scroll Min Interval:").pack(side=tk.LEFT)
        ttk.Entry(scroll_row, textvariable=self.mouse_scroll_min_interval, width=4).pack(side=tk.LEFT, padx=2)
        ttk.Label(scroll_row, text="Scroll Max Interval:").pack(side=tk.LEFT)
        ttk.Entry(scroll_row, textvariable=self.mouse_scroll_max_interval, width=4).pack(side=tk.LEFT, padx=2)

        # Keyboard Tab
        keyboard_tab = ttk.Frame(notebook)
        notebook.add(keyboard_tab, text="⌨️ Keyboard")
        tk.Label(keyboard_tab, text="Keyboard Activity", font="Helvetica 11 bold", pady=6).pack(anchor='w', padx=10, pady=(10,0))
        keyboard_toggle = ttk.Checkbutton(keyboard_tab, text="Enable Keyboard Simulation", variable=self.keyboard_enabled)
        keyboard_toggle.pack(anchor='w', padx=20, pady=2)
        row = ttk.Frame(keyboard_tab)
        row.pack(fill='x', pady=3, padx=10)
        ttk.Label(row, text="Actions:").pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.keyboard_actions, width=5).pack(side=tk.LEFT, padx=3)
        ttk.Label(row, text="Phrases (comma separated):").pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.keyboard_phrases, width=30).pack(side=tk.LEFT, padx=3)
        # Intervals
        interval_row = ttk.Frame(keyboard_tab)
        interval_row.pack(fill='x', pady=3, padx=10)
        ttk.Label(interval_row, text="Min Interval:").pack(side=tk.LEFT)
        ttk.Entry(interval_row, textvariable=self.keyboard_min_interval, width=4).pack(side=tk.LEFT, padx=2)
        ttk.Label(interval_row, text="Max Interval:").pack(side=tk.LEFT)
        ttk.Entry(interval_row, textvariable=self.keyboard_max_interval, width=4).pack(side=tk.LEFT, padx=2)
        # Dart/code writing
        code_row = ttk.Frame(keyboard_tab)
        code_row.pack(fill='x', pady=3, padx=10)
        ttk.Checkbutton(code_row, text="Enable Dart Mode", variable=self.dart_enabled).pack(side=tk.LEFT, padx=2)
        ttk.Label(code_row, text="Dart Lines:").pack(side=tk.LEFT)
        ttk.Entry(code_row, textvariable=self.dart_lines, width=4).pack(side=tk.LEFT, padx=2)
        ttk.Checkbutton(code_row, text="Enable Code Writing", variable=self.code_writing_enabled).pack(side=tk.LEFT, padx=2)

        # Browser Tab
        browser_tab = ttk.Frame(notebook)
        notebook.add(browser_tab, text="🌐 Browser")
        tk.Label(browser_tab, text="Browser Activity", font="Helvetica 11 bold", pady=6).pack(anchor='w', padx=10, pady=(10,0))
        browser_toggle = ttk.Checkbutton(browser_tab, text="Enable Browser Simulation", variable=self.browser_enabled)
        browser_toggle.pack(anchor='w', padx=20, pady=2)
        row = ttk.Frame(browser_tab)
        row.pack(fill='x', pady=3, padx=10)
        ttk.Label(row, text="Headless:").pack(side=tk.LEFT)
        ttk.Checkbutton(row, variable=self.browser_headless).pack(side=tk.LEFT, padx=2)
        ttk.Label(row, text="Min Interval:").pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.browser_min_interval, width=4).pack(side=tk.LEFT, padx=2)
        ttk.Label(row, text="Max Interval:").pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.browser_max_interval, width=4).pack(side=tk.LEFT, padx=2)

        # Advanced Tab
        advanced_tab = ttk.Frame(notebook)
        notebook.add(advanced_tab, text="⚙️ Advanced")
        tk.Label(advanced_tab, text="Advanced & UI Settings", font="Helvetica 11 bold", pady=6).pack(anchor='w', padx=10, pady=(10,0))
        ttk.Checkbutton(advanced_tab, text="Auto-Restart Simulation", variable=self.auto_restart_var).pack(anchor='w', padx=20, pady=2)
        ttk.Label(advanced_tab, text="Idle Timeout (min):").pack(anchor='w', padx=20, pady=2)
        ttk.Entry(advanced_tab, textvariable=self.idle_timeout_var, width=4).pack(anchor='w', padx=20, pady=2)
        ttk.Checkbutton(advanced_tab, text="Enable Hotkey Control", variable=self.hotkey_control_var).pack(anchor='w', padx=20, pady=2)
        ttk.Checkbutton(advanced_tab, text="Enable Notifications", variable=self.notifications_enabled).pack(anchor='w', padx=20, pady=2)
        ttk.Checkbutton(advanced_tab, text="Minimize on Start", variable=self.minimize_on_start_var).pack(anchor='w', padx=20, pady=2)

        # --- Log/Output Panel ---
        log_frame = ttk.Frame(self.root)
        log_frame.pack(fill='both', expand=False, padx=15, pady=(0,10))
        tk.Label(log_frame, text="Log Output", font="Helvetica 10 bold").pack(anchor='w')
        self.log_text = tk.Text(log_frame, height=6, state='normal', wrap='word')
        self.log_text.pack(fill='both', expand=True)
        self.log_text.config(state='disabled')

    def apply_theme(self):
        # Update dark mode toggle button text if present
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button) and (child['text'].startswith('🌙') or child['text'].startswith('☀️')):
                        child['text'] = "🌙 Dark Mode" if not self.is_dark_mode else "☀️ Light Mode"
        if self.is_dark_mode:
            self.root.configure(bg=self.glassy_bg_dark)
            style = ttk.Style()
            style.theme_use('clam')  # Use a theme that supports better customization
            style.configure("TNotebook", background=self.glassy_bg_dark, foreground='white', fieldbackground=self.glassy_bg_dark, bordercolor='#333333')
            style.configure("TNotebook.Tab", background='#2A2A2E', foreground='white', padding=[8, 4], bordercolor='#333333')
            style.map("TNotebook.Tab", background=[('selected', self.glassy_accent_dark)], foreground=[('selected', 'white')])
            style.configure("TFrame", background=self.glassy_bg_dark, foreground='white')
            style.configure("TLabel", background=self.glassy_bg_dark, foreground='white', font="Helvetica 10")
            style.configure("TButton", background=self.glassy_accent_dark, foreground='white', bordercolor='#005a9e', padding=(8, 4))
            style.map("TButton", background=[('active', '#005a9e')])
            style.configure("Control.TButton", background=self.glassy_accent_dark, foreground='white', bordercolor='#005a9e', padding=(8, 4))
            style.map("Control.TButton", background=[('active', '#005a9e')])
            style.configure("TCheckbutton", background=self.glassy_bg_dark, foreground='white')
            style.configure("TEntry", background='#333333', foreground='white', fieldbackground='#333333', bordercolor='#444444', font="Helvetica 10")
            style.configure("TText", background='#333333', foreground='white', font="Helvetica 10")
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.configure(foreground='white')
            if hasattr(self, 'log_text') and self.log_text:
                self.log_text.configure(bg='#333333', fg='white', insertbackground='white')
            style.configure("StatusBar.TFrame", background="#23272e")
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.configure(foreground='white', background="#23272e", font="Helvetica 9")
        else:
            self.root.configure(bg=self.glassy_bg_light)
            style = ttk.Style()
            style.theme_use('clam')  # Use a theme that supports better customization
            style.configure("TNotebook", background=self.glassy_bg_light, foreground='black', fieldbackground=self.glassy_bg_light, bordercolor='#d0d0d0')
            style.configure("TNotebook.Tab", background='#E5E5E7', foreground='black', padding=[8, 4], bordercolor='#d0d0d0')
            style.map("TNotebook.Tab", background=[('selected', self.glassy_accent_light)], foreground=[('selected', 'white')])
            style.configure("TFrame", background=self.glassy_bg_light, foreground='black')
            style.configure("TLabel", background=self.glassy_bg_light, foreground='black', font="Helvetica 10")
            style.configure("TButton", background=self.glassy_accent_light, foreground='white', bordercolor='#005a9e', padding=(8, 4))
            style.map("TButton", background=[('active', '#005a9e')])
            style.configure("Control.TButton", background=self.glassy_accent_light, foreground='white', bordercolor='#005a9e', padding=(8, 4))
            style.map("Control.TButton", background=[('active', '#005a9e')])
            style.configure("TCheckbutton", background=self.glassy_bg_light, foreground='black')
            style.configure("TEntry", background='#ffffff', foreground='black', fieldbackground='#ffffff', bordercolor='#d0d0d0', font="Helvetica 10")
            style.configure("TText", background='#ffffff', foreground='black', font="Helvetica 10")
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.configure(foreground='black')
            if hasattr(self, 'log_text') and self.log_text:
                self.log_text.configure(bg='#ffffff', fg='black', insertbackground='black')
            style.configure("StatusBar.TFrame", background="#e8e8e8")
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.configure(foreground='black', background="#e8e8e8", font="Helvetica 9")

    def toggle_dark_mode(self):
        self.is_dark_mode = not self.is_dark_mode
        if 'ui' not in self.app.config:
            self.app.config['ui'] = {}
        self.app.config['ui']['dark_mode'] = self.is_dark_mode
        self.app.save_config()
        self.apply_theme()
