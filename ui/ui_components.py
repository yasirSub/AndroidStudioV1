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
        # UI variables
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

    def setup_ui(self):
        # Top bar with app title and dark mode
        top = ttk.Frame(self.root)
        top.pack(fill='x', pady=(5, 10))
        tk.Label(top, text="Android Studio v1.0.0", font="Helvetica 14 bold").pack(side=tk.LEFT, padx=(15,0))
        dark_toggle_btn = ttk.Button(top, text="🌙" if not self.is_dark_mode else "☀️", width=3, command=self.toggle_dark_mode)
        dark_toggle_btn.pack(side=tk.RIGHT, padx=(0,15))
        Tooltip(dark_toggle_btn, "Toggle dark/light mode.")

        # Tabbed layout with icons
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=15, pady=10)

        # Helper for minimal toggle buttons
        def make_toggle(parent, var, label, tooltip, command=None):
            def update_btn():
                btn.config(text=f"{label}: {'ON' if var.get() else 'OFF'}", style="Enabled.TButton" if var.get() else "Disabled.TButton")
            def toggle():
                var.set(not var.get())
                update_btn()
                if command:
                    command()
            btn = ttk.Button(parent, command=toggle, cursor="hand2")
            btn.pack(fill='x', pady=3, padx=10)
            Tooltip(btn, tooltip)
            update_btn()
            return btn

        style = ttk.Style()
        style.configure("Enabled.TButton", foreground="white", background=self.glassy_accent_light if not self.is_dark_mode else self.glassy_accent_dark, font="Helvetica 10 bold", borderwidth=0, relief="flat", padding=(8, 4))
        style.map("Enabled.TButton", background=[('active', '#005a9e')])
        style.configure("Disabled.TButton", foreground="#444" if not self.is_dark_mode else "#AAA", background="#e0e0e0" if not self.is_dark_mode else "#2A2A2E", font="Helvetica 10", borderwidth=0, relief="flat", padding=(8, 4))
        style.map("Disabled.TButton", background=[('active', '#cccccc' if not self.is_dark_mode else '#333333')])
        style.configure("Section.TLabel", font="Helvetica 11 bold", padding=(0,6,0,2))

        # Mouse Tab
        mouse_tab = ttk.Frame(notebook)
        notebook.add(mouse_tab, text="🖱️ Mouse")
        tk.Label(mouse_tab, text="Mouse Activity", font="Helvetica 11 bold", pady=6).pack(anchor='w', padx=10, pady=(10,0))
        make_toggle(mouse_tab, self.mouse_enabled, "Mouse Activity", "Enable or disable mouse activity.")
        row = ttk.Frame(mouse_tab)
        row.pack(fill='x', pady=3, padx=10)
        ttk.Label(row, text="Movements:").pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.mouse_movements, width=5).pack(side=tk.LEFT, padx=3)
        ttk.Label(row, text="Scrolls:").pack(side=tk.LEFT)
        scroll_entry = ttk.Entry(row, textvariable=self.mouse_scrolls, width=4)
        scroll_entry.pack(side=tk.LEFT, padx=3)
        Tooltip(scroll_entry, "Number of vertical scroll actions per mouse cycle.")
        ttk.Label(row, text="Scroll Sensitivity:").pack(side=tk.LEFT)
        scroll_sens_entry = ttk.Entry(row, textvariable=self.mouse_scroll_sensitivity, width=4)
        scroll_sens_entry.pack(side=tk.LEFT, padx=3)
        Tooltip(scroll_sens_entry, "How much each scroll action moves (lines per scroll).")
        ttk.Label(row, text="H-Scrolls:").pack(side=tk.LEFT)
        hscroll_entry = ttk.Entry(row, textvariable=self.mouse_hscrolls, width=4)
        hscroll_entry.pack(side=tk.LEFT, padx=3)
        Tooltip(hscroll_entry, "Number of horizontal scroll actions per mouse cycle.")
        # Scroll interval row
        scroll_row = ttk.Frame(mouse_tab)
        scroll_row.pack(fill='x', pady=3, padx=10)
        ttk.Label(scroll_row, text="Scroll Min Interval:").pack(side=tk.LEFT)
        ttk.Entry(scroll_row, textvariable=self.mouse_scroll_min_interval, width=4).pack(side=tk.LEFT, padx=2)
        ttk.Label(scroll_row, text="Scroll Max Interval:").pack(side=tk.LEFT)
        ttk.Entry(scroll_row, textvariable=self.mouse_scroll_max_interval, width=4).pack(side=tk.LEFT, padx=2)
        Tooltip(scroll_row, "Random delay between scrolls for realism.")

        # Keyboard Tab
        keyboard_tab = ttk.Frame(notebook)
        notebook.add(keyboard_tab, text="⌨️ Keyboard")
        tk.Label(keyboard_tab, text="Keyboard Activity", font="Helvetica 11 bold", pady=6).pack(anchor='w', padx=10, pady=(10,0))
        make_toggle(keyboard_tab, self.keyboard_enabled, "Keyboard Activity", "Enable or disable keyboard activity.")
        row = ttk.Frame(keyboard_tab)
        row.pack(fill='x', pady=3, padx=10)
        ttk.Label(row, text="Actions:").pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.keyboard_actions, width=5).pack(side=tk.LEFT, padx=3)
        ttk.Label(row, text="Phrases:").pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.keyboard_phrases, width=20).pack(side=tk.LEFT, padx=3)
        make_toggle(keyboard_tab, self.dart_enabled, "Dart Code", "Enable or disable Dart code simulation.")
        make_toggle(keyboard_tab, self.code_writing_enabled, "Code Writing Loop", "Enable or disable automatic code writing and erasing loop.")

        # Browser Tab
        browser_tab = ttk.Frame(notebook)
        notebook.add(browser_tab, text="🌐 Browser")
        tk.Label(browser_tab, text="Browser Activity", font="Helvetica 11 bold", pady=6).pack(anchor='w', padx=10, pady=(10,0))
        make_toggle(browser_tab, self.browser_enabled, "Browser Activity", "Enable or disable browser activity.")
        make_toggle(browser_tab, self.browser_headless, "Headless Mode", "Run browser in headless (no window) mode.")

        # System Tab
        system_tab = ttk.Frame(notebook)
        notebook.add(system_tab, text="⚙️ System")
        tk.Label(system_tab, text="System Settings", font="Helvetica 11 bold", pady=6).pack(anchor='w', padx=10, pady=(10,0))
        make_toggle(system_tab, self.auto_restart_var, "Auto-Restart", "Automatically restart after user inactivity.", self.app.toggle_auto_restart)
        make_toggle(system_tab, self.hotkey_control_var, "Hotkey Control", "Enable or disable global hotkeys.", self.app.toggle_hotkey_control)
        make_toggle(system_tab, self.notifications_enabled, "Notifications", "Show pop-up notifications for important events.", self.app.toggle_notifications)
        make_toggle(system_tab, self.minimize_on_start_var, "Minimize to Tray on Start", "If enabled, the app will start minimized to the system tray.", self.app.toggle_minimize_on_start)
        row = ttk.Frame(system_tab)
        row.pack(fill='x', pady=3, padx=10)
        ttk.Label(row, text="Idle Timeout (min):").pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.idle_timeout_var, width=4).pack(side=tk.LEFT, padx=3)
        ttk.Button(row, text="Apply", command=self.app.update_idle_timeout).pack(side=tk.LEFT, padx=5)

        # About Tab
        about_tab = ttk.Frame(notebook)
        notebook.add(about_tab, text="ℹ️ About")
        tk.Label(about_tab, text="About Android Studio", font="Helvetica 11 bold", pady=6).pack(anchor='w', padx=10, pady=(10,0))
        tk.Label(about_tab, text="Version: 1.0.0", font="Helvetica 10").pack(anchor='w', padx=10, pady=2)
        tk.Label(about_tab, text="Made by: Yasir Subhani", font="Helvetica 10").pack(anchor='w', padx=10, pady=2)
        tk.Label(about_tab, text="GitHub Repository:", font="Helvetica 10").pack(anchor='w', padx=10, pady=2)
        repo_link = tk.Label(about_tab, text="https://github.com/yasirSub", font="Helvetica 10 underline", foreground=self.glassy_accent_light if not self.is_dark_mode else self.glassy_accent_dark, cursor="hand2")
        repo_link.pack(anchor='w', padx=10, pady=2)
        repo_link.bind("<Button-1>", lambda e: self.app.open_url("https://github.com/yasirSub"))
        Tooltip(repo_link, "Click to open repository in browser.")
        
        # Logs Tab
        logs_tab = ttk.Frame(notebook)
        notebook.add(logs_tab, text="📝 Logs")
        tk.Label(logs_tab, text="Log Output", font="Helvetica 11 bold", pady=6).pack(anchor='w', padx=10, pady=(10,0))
        self.log_text = tk.Text(logs_tab, height=12, wrap='word', font="Helvetica 9", state='normal')
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(logs_tab, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text['yscrollcommand'] = scrollbar.set
        self.app.update_log_display()

        # Controls
        ctrl = ttk.Frame(self.root)
        ctrl.pack(fill='x', pady=10, padx=15)
        for text, command in [
            ("Save", self.app.update_config),
            ("Apply", self.app.apply_changes),
            ("Start", self.app.start_simulation),
            ("Stop", self.app.stop_simulation),
            ("Minimize", self.app.system_tray.minimize_to_tray),
            ("Exit", self.app.exit_application)
        ]:
            ttk.Button(ctrl, text=text, command=command, cursor="hand2", style="Control.TButton").pack(side=tk.LEFT, padx=5, expand=True, fill='x')

        # Status Bar (fixed at bottom, visually separated)
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill='x')
        self.status_label = ttk.Label(status_frame, text="Status: Simulation Stopped", anchor='w', font="Helvetica 9")
        self.status_label.pack(fill='x', pady=(0, 5), padx=15)
        status_frame.configure(style="StatusBar.TFrame")

        # Set window icon if available
        try:
            self.root.iconbitmap('Android_Studio_icon_(2023).ico')
        except Exception:
            pass
