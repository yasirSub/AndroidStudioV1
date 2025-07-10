import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from typing import Optional, Callable, Any

class ModernTooltip:
    """Modern tooltip with better styling and positioning"""
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tip_window = None
        self.id = None
        self.widget.bind("<Enter>", self.schedule_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def schedule_tip(self, event=None):
        self.id = self.widget.after(self.delay, self.show_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        
        x, y, _, cy = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        # Modern tooltip styling
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                        background="#2D3748", foreground="#FFFFFF",
                        relief=tk.FLAT, borderwidth=0,
                        font=("Segoe UI", 9), padx=8, pady=4)
        label.pack()
        
        # Add subtle shadow effect
        tw.configure(bg="#2D3748")

    def hide_tip(self, event=None):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

class ModernButton(tk.Button):
    """Modern button with hover effects and consistent styling"""
    def __init__(self, master, text, command: Optional[Callable[[], Any]] = None, style="primary", **kwargs):
        self.style = style
        self.colors = {
            "primary": {"bg": "#3182CE", "fg": "#FFFFFF", "active_bg": "#2C5AA0", "active_fg": "#FFFFFF"},
            "secondary": {"bg": "#718096", "fg": "#FFFFFF", "active_bg": "#4A5568", "active_fg": "#FFFFFF"},
            "success": {"bg": "#38A169", "fg": "#FFFFFF", "active_bg": "#2F855A", "active_fg": "#FFFFFF"},
            "danger": {"bg": "#E53E3E", "fg": "#FFFFFF", "active_bg": "#C53030", "active_fg": "#FFFFFF"},
            "warning": {"bg": "#D69E2E", "fg": "#FFFFFF", "active_bg": "#B7791F", "active_fg": "#FFFFFF"}
        }
        if command is None:
            command = lambda: None
        colors = self.colors.get(style, self.colors["primary"])
        super().__init__(
            master, text=text, command=command,
            font=("Segoe UI", 10, "bold"),
            bg=colors["bg"], fg=colors["fg"],
            activebackground=colors["active_bg"], activeforeground=colors["active_fg"],
            relief=tk.FLAT, borderwidth=0, padx=16, pady=8,
            cursor="hand2", **kwargs
        )
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        colors = self.colors.get(self.style, self.colors["primary"])
        self.configure(bg=colors["active_bg"])

    def on_leave(self, event):
        colors = self.colors.get(self.style, self.colors["primary"])
        self.configure(bg=colors["bg"])

class ModernSlider(tk.Frame):
    """Modern slider with label and value display"""
    def __init__(self, master, label, variable, from_=0, to=100, resolution=1, is_float=False, fg: str = "#000000", bg: str = "#FFFFFF", **kwargs):
        super().__init__(master, bg=bg)
        
        # Label
        self.label = tk.Label(self, text=label, font=("Segoe UI", 10), fg=fg, bg=bg)
        self.label.pack(anchor='w', pady=(0, 4))
        
        # Slider frame
        slider_frame = tk.Frame(self, bg=bg)
        slider_frame.pack(fill='x', pady=2)
        
        # Slider
        if is_float:
            self.slider = tk.Scale(
                slider_frame, from_=float(from_), to=float(to), resolution=float(resolution),  # type: ignore[reportArgumentType]
                orient=tk.HORIZONTAL, variable=variable, showvalue=False,
                bg=bg, fg=fg, troughcolor="#E2E8F0",
                highlightthickness=0, length=200, **kwargs
            )
        else:
            self.slider = tk.Scale(
                slider_frame, from_=int(from_), to=int(to), resolution=int(resolution),
                orient=tk.HORIZONTAL, variable=variable, showvalue=False,
                bg=bg, fg=fg, troughcolor="#E2E8F0",
                highlightthickness=0, length=200, **kwargs
            )
        self.slider.pack(side=tk.LEFT, padx=(0, 8))
        
        # Value label
        self.value_label = tk.Label(slider_frame, text=str(variable.get()),
                                   font=("Segoe UI", 10, "bold"),
                                   fg=fg, bg=bg, width=6)
        self.value_label.pack(side=tk.LEFT)
        
        # Update value label when slider changes
        def update_label(*args):
            self.value_label.config(text=str(variable.get()))
        variable.trace('w', update_label)

class ModernEntry(tk.Frame):
    """Modern entry with label"""
    def __init__(self, master, label, variable, width=10, fg: str = "#000000", bg: str = "#FFFFFF", **kwargs):
        super().__init__(master, bg=bg)
        
        # Label
        self.label = tk.Label(self, text=label, font=("Segoe UI", 10), fg=fg, bg=bg)
        self.label.pack(anchor='w', pady=(0, 4))
        
        # Entry
        self.entry = tk.Entry(self, textvariable=variable, width=width,
                             font=("Segoe UI", 10), relief=tk.FLAT,
                             bg=bg, fg=fg, insertbackground="#3182CE",
                             highlightthickness=1, highlightcolor="#3182CE",
                             highlightbackground="#E2E8F0", **kwargs)
        self.entry.pack(fill='x', pady=2)

class ModernCheckbox(tk.Frame):
    """Modern checkbox with label"""
    def __init__(self, master, text, variable, **kwargs):
        super().__init__(master, bg=master.cget("bg") if hasattr(master, 'cget') else "#FFFFFF")
        
        self.checkbox = ttk.Checkbutton(self, text=text, variable=variable, **kwargs)
        self.checkbox.pack(anchor='w', pady=2)

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
        
        self._tilde_down_time = 0
        self._tilde_press_times = []

        # Color schemes
        self.colors = {
            'light': {
                'bg': '#F7FAFC',
                'card_bg': '#FFFFFF',
                'primary': '#3182CE',
                'secondary': '#718096',
                'success': '#38A169',
                'warning': '#D69E2E',
                'danger': '#E53E3E',
                'text': '#2D3748',
                'text_secondary': '#4A5568',
                'border': '#E2E8F0',
                'hover': '#EDF2F7'
            },
            'dark': {
                'bg': '#1A202C',
                'card_bg': '#2D3748',
                'primary': '#63B3ED',
                'secondary': '#A0AEC0',
                'success': '#68D391',
                'warning': '#F6E05E',
                'danger': '#FC8181',
                'text': '#F7FAFC',
                'text_secondary': '#E2E8F0',
                'border': '#4A5568',
                'hover': '#4A5568'
            }
        }

    def get_color(self, color_name):
        """Get color based on current theme"""
        theme = 'dark' if self.is_dark_mode else 'light'
        return self.colors[theme].get(color_name, '#000000')

    def get_fg_bg(self):
        """Return (fg, bg) tuple for current theme for high contrast text"""
        if self.is_dark_mode:
            return (self.colors['dark']['text'], self.colors['dark']['card_bg'])
        else:
            return (self.colors['light']['text'], self.colors['light']['card_bg'])

    def apply_theme(self):
        """Apply the current theme to the application"""
        self.root.configure(bg=self.get_color('bg'))
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure common styles
        style.configure("TFrame", background=self.get_color('bg'))
        style.configure("TLabel", background=self.get_color('bg'), foreground=self.get_color('text'))
        style.configure("TButton", background=self.get_color('primary'), foreground='#FFFFFF')
        style.configure("TCheckbutton", background=self.get_color('bg'), foreground=self.get_color('text'))
        style.configure("TEntry", background=self.get_color('card_bg'), foreground=self.get_color('text'))
        style.configure("TText", background=self.get_color('card_bg'), foreground=self.get_color('text'))

    def toggle_dark_mode(self):
        """Toggle between dark and light mode"""
        self.is_dark_mode = not self.is_dark_mode
        if 'ui' not in self.app.config:
            self.app.config['ui'] = {}
        self.app.config['ui']['dark_mode'] = self.is_dark_mode
        self.app.save_config()
        self.apply_theme()

    def test_mouse_move(self):
        """Test mouse movement with current settings"""
        try:
            import pyautogui  # type: ignore
            import random
            x, y = pyautogui.position()
            screen_width, screen_height = pyautogui.size()
            end_x = random.randint(int(screen_width * 0.2), int(screen_width * 0.8))
            end_y = random.randint(int(screen_height * 0.2), int(screen_height * 0.8))
            pyautogui.moveTo(end_x, end_y, duration=self.mouse_min_duration.get())
            messagebox.showinfo("Test Complete", "Mouse movement test completed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to test mouse movement: {e}")

    def test_pause_settings(self):
        """Test pause settings without saving"""
        if hasattr(self.app.simulation_controls, 'resume_timer') and self.app.simulation_controls.resume_timer:
            self.app.root.after_cancel(self.app.simulation_controls.resume_timer)
            self.app.simulation_controls.resume_timer = None
        self.app.simulation_controls.pause_duration = self.pause_after_activity_var.get()
        messagebox.showinfo("Test", f"Pause after activity set to {self.pause_after_activity_var.get()} seconds (not saved)")

    def apply_pause_settings(self):
        """Apply and save pause settings"""
        if 'ui' not in self.app.config:
            self.app.config['ui'] = {}
        self.app.config['ui']['pause_after_activity'] = self.pause_after_activity_var.get()
        self.app.save_config()
        self.app.simulation_controls.pause_duration = self.pause_after_activity_var.get()
        messagebox.showinfo("Applied", f"Pause after activity set to {self.pause_after_activity_var.get()} seconds and saved.")

    def refresh_log(self):
        """Refresh the log display"""
        self.app.update_log_display()

    def clear_log(self):
        """Clear all log messages"""
        self.app.log_messages.clear()
        self.app.update_log_display()

    def show_config(self):
        """Show current configuration in a popup"""
        import json
        config_str = json.dumps(self.app.config, indent=2)
        
        top = tk.Toplevel(self.root)
        top.title("Current Configuration")
        top.geometry('700x500')
        top.configure(bg=self.get_color('bg'))
        
        # Make it modal
        top.transient(self.root)
        top.grab_set()
        
        # Text widget
        fg, bg = self.get_fg_bg()
        text = tk.Text(top, wrap='word', font=("Consolas", 10),
                      bg=bg, fg=fg)
        text.insert('1.0', config_str)
        text.pack(fill='both', expand=True, padx=10, pady=10)
        text.config(state='disabled')
        
        # Close button
        close_btn = ModernButton(top, "Close", top.destroy, "primary")
        close_btn.pack(pady=10)

    def save_config_as(self):
        """Save configuration to a file"""
        from tkinter import filedialog
        import json
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.app.config, f, indent=2)
                messagebox.showinfo("Success", f"Configuration saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration: {e}")

    def setup_ui(self):
        """Setup the main UI with modern design"""
        self.apply_theme()
        
        # Main container
        main_container = tk.Frame(self.root, bg=self.get_color('bg'))
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header section
        self.create_header(main_container)
        
        # Content section
        content_frame = tk.Frame(main_container, bg=self.get_color('bg'))
        content_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        # Create notebook for tabs
        self.create_notebook(content_frame)
        
        # Footer section
        self.create_footer(main_container)

    def create_header(self, parent):
        """Create the header with status and controls"""
        header_frame = tk.Frame(parent, bg=self.get_color('card_bg'), relief=tk.FLAT, bd=0)
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Status section
        status_frame = tk.Frame(header_frame, bg=self.get_color('card_bg'))
        status_frame.pack(side=tk.LEFT, padx=20, pady=20)
        
        fg, bg = self.get_fg_bg()
        self.status_label = tk.Label(
            status_frame, text="🟢 Status: Ready", 
            font=("Segoe UI", 16, "bold"),
            fg=fg, bg=bg
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Control buttons
        controls_frame = tk.Frame(header_frame, bg=self.get_color('card_bg'))
        controls_frame.pack(side=tk.RIGHT, padx=20, pady=20)
        
        ModernButton(controls_frame, "▶ Start", self.app.start_simulation, "success").pack(side=tk.LEFT, padx=5)
        ModernButton(controls_frame, "⏸ Pause", lambda: self.app.simulation_controls.handle_user_activity(), "warning").pack(side=tk.LEFT, padx=5)
        ModernButton(controls_frame, "■ Stop", self.app.stop_simulation, "danger").pack(side=tk.LEFT, padx=5)
        ModernButton(controls_frame, "🗕 Minimize to Tray", lambda: self.app.system_tray.minimize_to_tray(), "secondary").pack(side=tk.LEFT, padx=5)
        
        # Theme toggle
        theme_btn = ModernButton(
            controls_frame, "🌙" if not self.is_dark_mode else "☀️", 
            self.toggle_dark_mode, "secondary"
        )
        theme_btn.pack(side=tk.LEFT, padx=(15, 0))
        ModernTooltip(theme_btn, "Toggle dark/light mode")

    def create_notebook(self, parent):
        """Create the tabbed interface"""
        style = ttk.Style()
        style.configure("Modern.TNotebook", background=self.get_color('bg'), borderwidth=0)
        style.configure("Modern.TNotebook.Tab", 
                       background=self.get_color('card_bg'),
                       foreground=self.get_color('text'),
                       padding=[20, 10],
                       font=("Segoe UI", 12, "bold"))
        style.map("Modern.TNotebook.Tab",
                 background=[('selected', self.get_color('primary'))],
                 foreground=[('selected', '#FFFFFF')])
        
        self.notebook = ttk.Notebook(parent, style="Modern.TNotebook")
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.create_mouse_tab()
        self.create_keyboard_tab()
        self.create_browser_tab()
        self.create_advanced_tab()
        self.create_log_tab()

    def create_mouse_tab(self):
        """Create the mouse settings tab"""
        mouse_frame = tk.Frame(self.notebook, bg=self.get_color('bg'))
        self.notebook.add(mouse_frame, text="🖱️ Mouse")
        
        # Scrollable content
        canvas = tk.Canvas(mouse_frame, bg=self.get_color('bg'), highlightthickness=0)
        scrollbar = ttk.Scrollbar(mouse_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.get_color('bg'))
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Content
        content_frame = tk.Frame(scrollable_frame, bg=self.get_color('bg'))
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        fg, bg = self.get_fg_bg()
        title = tk.Label(content_frame, text="Mouse Activity Settings", 
                        font=("Segoe UI", 18, "bold"),
                        fg=fg, bg=bg)
        title.pack(anchor='w', pady=(0, 20))
        
        # Enable toggle
        ModernCheckbox(content_frame, "Enable Mouse Activity", self.mouse_enabled).pack(anchor='w', pady=5)
        
        # Settings grid
        settings_frame = tk.Frame(content_frame, bg=self.get_color('bg'))
        settings_frame.pack(fill='x', pady=20)
        
        # Row 1
        row1 = tk.Frame(settings_frame, bg=self.get_color('bg'))
        row1.pack(fill='x', pady=10)
        fg, bg = self.get_fg_bg()
        ModernSlider(row1, "Mouse Movements per Session", self.mouse_movements, from_=1, to=50, resolution=1, is_float=False, fg=fg, bg=bg).pack(side=tk.LEFT, padx=(0, 20))
        fg, bg = self.get_fg_bg()
        ModernSlider(row1, "Scroll Sensitivity", self.mouse_scroll_sensitivity, from_=1, to=20, resolution=1, is_float=False, fg=fg, bg=bg).pack(side=tk.LEFT)
        # Row 2
        row2 = tk.Frame(settings_frame, bg=self.get_color('bg'))
        row2.pack(fill='x', pady=10)
        fg, bg = self.get_fg_bg()
        ModernSlider(row2, "Min Duration (seconds)", self.mouse_min_duration, from_=0.1, to=5.0, resolution=0.1, is_float=True, fg=fg, bg=bg).pack(side=tk.LEFT, padx=(0, 20))  # type: ignore[reportArgumentType]
        fg, bg = self.get_fg_bg()
        ModernSlider(row2, "Max Duration (seconds)", self.mouse_max_duration, from_=0.5, to=10.0, resolution=0.1, is_float=True, fg=fg, bg=bg).pack(side=tk.LEFT)  # type: ignore[reportArgumentType]
        # Row 3
        row3 = tk.Frame(settings_frame, bg=self.get_color('bg'))
        row3.pack(fill='x', pady=10)
        fg, bg = self.get_fg_bg()
        ModernSlider(row3, "Min Interval (seconds)", self.mouse_min_interval, from_=0.5, to=10.0, resolution=0.1, is_float=True, fg=fg, bg=bg).pack(side=tk.LEFT, padx=(0, 20))  # type: ignore[reportArgumentType]
        fg, bg = self.get_fg_bg()
        ModernSlider(row3, "Max Interval (seconds)", self.mouse_max_interval, from_=1.0, to=20.0, resolution=0.1, is_float=True, fg=fg, bg=bg).pack(side=tk.LEFT)  # type: ignore[reportArgumentType]
        
        # Advanced settings
        advanced_frame = tk.Frame(content_frame, bg=self.get_color('card_bg'), relief=tk.FLAT, bd=1)
        advanced_frame.pack(fill='x', pady=20, ipady=15, ipadx=15)
        
        fg, bg = self.get_fg_bg()
        tk.Label(advanced_frame, text="Advanced Mouse Settings", 
                font=("Segoe UI", 12, "bold"),
                fg=fg, bg=bg).pack(anchor='w', pady=(0, 10))
        
        # Advanced grid
        adv_row1 = tk.Frame(advanced_frame, bg=self.get_color('card_bg'))
        adv_row1.pack(fill='x', pady=5)
        
        fg, bg = self.get_fg_bg()
        ModernEntry(adv_row1, "Scrolls per Session", self.mouse_scrolls, width=8, fg=fg, bg=bg).pack(side=tk.LEFT, padx=(0, 20))
        fg, bg = self.get_fg_bg()
        ModernEntry(adv_row1, "Horizontal Scrolls", self.mouse_hscrolls, width=8, fg=fg, bg=bg).pack(side=tk.LEFT, padx=(0, 20))
        fg, bg = self.get_fg_bg()
        ModernEntry(adv_row1, "Scroll Min Interval", self.mouse_scroll_min_interval, width=8, fg=fg, bg=bg).pack(side=tk.LEFT)
        
        # Test button
        test_btn = ModernButton(content_frame, "Test Mouse Movement", self.test_mouse_move, "primary")
        test_btn.pack(anchor='w', pady=20)
        ModernTooltip(test_btn, "Test the current mouse settings")
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_keyboard_tab(self):
        """Create the keyboard settings tab"""
        keyboard_frame = tk.Frame(self.notebook, bg=self.get_color('bg'))
        self.notebook.add(keyboard_frame, text="⌨️ Keyboard")
        
        # Scrollable content
        canvas = tk.Canvas(keyboard_frame, bg=self.get_color('bg'), highlightthickness=0)
        scrollbar = ttk.Scrollbar(keyboard_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.get_color('bg'))
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Content
        content_frame = tk.Frame(scrollable_frame, bg=self.get_color('bg'))
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        fg, bg = self.get_fg_bg()
        title = tk.Label(content_frame, text="Keyboard Activity Settings", 
                        font=("Segoe UI", 18, "bold"),
                        fg=fg, bg=bg)
        title.pack(anchor='w', pady=(0, 20))
        
        # Enable toggle
        ModernCheckbox(content_frame, "Enable Keyboard Activity", self.keyboard_enabled).pack(anchor='w', pady=5)
        
        # Settings
        settings_frame = tk.Frame(content_frame, bg=self.get_color('bg'))
        settings_frame.pack(fill='x', pady=20)
        
        # Row 1
        row1 = tk.Frame(settings_frame, bg=self.get_color('bg'))
        row1.pack(fill='x', pady=10)
        fg, bg = self.get_fg_bg()
        ModernSlider(row1, "Actions per Session", self.keyboard_actions, from_=1, to=50, resolution=1, is_float=False, fg=fg, bg=bg).pack(side=tk.LEFT, padx=(0, 20))
        fg, bg = self.get_fg_bg()
        ModernSlider(row1, "Min Interval (seconds)", self.keyboard_min_interval, from_=1.0, to=30.0, resolution=0.5, is_float=True, fg=fg, bg=bg).pack(side=tk.LEFT)  # type: ignore[reportArgumentType]
        # Row 2
        row2 = tk.Frame(settings_frame, bg=self.get_color('bg'))
        row2.pack(fill='x', pady=10)
        fg, bg = self.get_fg_bg()
        ModernSlider(row2, "Max Interval (seconds)", self.keyboard_max_interval, from_=2.0, to=60.0, resolution=0.5, is_float=True, fg=fg, bg=bg).pack(side=tk.LEFT)  # type: ignore[reportArgumentType]
        
        # Phrases entry
        phrases_frame = tk.Frame(content_frame, bg=self.get_color('bg'))
        phrases_frame.pack(fill='x', pady=20)
        
        fg, bg = self.get_fg_bg()
        tk.Label(phrases_frame, text="Typing Phrases (comma separated)", 
                font=("Segoe UI", 10, "bold"),
                fg=fg, bg=bg).pack(anchor='w', pady=(0, 5))
        
        phrases_entry = tk.Text(phrases_frame, height=3, font=("Segoe UI", 10),
                               bg=self.get_color('card_bg'), fg=self.get_color('text'),
                               relief=tk.FLAT, borderwidth=1, highlightthickness=1,
                               highlightcolor=self.get_color('primary'),
                               highlightbackground=self.get_color('border'))
        phrases_entry.pack(fill='x', pady=5)
        phrases_entry.insert('1.0', self.keyboard_phrases.get())
        
        # Advanced options
        advanced_frame = tk.Frame(content_frame, bg=self.get_color('card_bg'), relief=tk.FLAT, bd=1)
        advanced_frame.pack(fill='x', pady=20, ipady=15, ipadx=15)
        
        fg, bg = self.get_fg_bg()
        tk.Label(advanced_frame, text="Advanced Keyboard Options", 
                font=("Segoe UI", 12, "bold"),
                fg=fg, bg=bg).pack(anchor='w', pady=(0, 10))
        
        ModernCheckbox(advanced_frame, "Enable Dart Mode", self.dart_enabled).pack(anchor='w', pady=2)
        ModernCheckbox(advanced_frame, "Enable Code Writing", self.code_writing_enabled).pack(anchor='w', pady=2)
        
        dart_row = tk.Frame(advanced_frame, bg=self.get_color('card_bg'))
        dart_row.pack(fill='x', pady=10)
        
        fg, bg = self.get_fg_bg()
        ModernEntry(dart_row, "Dart Lines", self.dart_lines, width=8, fg=fg, bg=bg).pack(side=tk.LEFT)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_browser_tab(self):
        """Create the browser settings tab"""
        browser_frame = tk.Frame(self.notebook, bg=self.get_color('bg'))
        self.notebook.add(browser_frame, text="🌐 Browser")
        
        content_frame = tk.Frame(browser_frame, bg=self.get_color('bg'))
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        fg, bg = self.get_fg_bg()
        title = tk.Label(content_frame, text="Browser Activity Settings", 
                        font=("Segoe UI", 18, "bold"),
                        fg=fg, bg=bg)
        title.pack(anchor='w', pady=(0, 20))
        
        # Enable toggle
        ModernCheckbox(content_frame, "Enable Browser Activity", self.browser_enabled).pack(anchor='w', pady=5)
        
        # Settings
        settings_frame = tk.Frame(content_frame, bg=self.get_color('bg'))
        settings_frame.pack(fill='x', pady=20)
        
        # Row 1
        row1 = tk.Frame(settings_frame, bg=self.get_color('bg'))
        row1.pack(fill='x', pady=10)
        fg, bg = self.get_fg_bg()
        ModernSlider(row1, "Min Interval (seconds)", self.browser_min_interval, from_=5.0, to=60.0, resolution=1.0, is_float=True, fg=fg, bg=bg).pack(side=tk.LEFT, padx=(0, 20))  # type: ignore[reportArgumentType]
        fg, bg = self.get_fg_bg()
        ModernSlider(row1, "Max Interval (seconds)", self.browser_max_interval, from_=10.0, to=120.0, resolution=1.0, is_float=True, fg=fg, bg=bg).pack(side=tk.LEFT)  # type: ignore[reportArgumentType]
        
        # Options
        options_frame = tk.Frame(content_frame, bg=self.get_color('card_bg'), relief=tk.FLAT, bd=1)
        options_frame.pack(fill='x', pady=20, ipady=15, ipadx=15)
        
        fg, bg = self.get_fg_bg()
        tk.Label(options_frame, text="Browser Options", 
                font=("Segoe UI", 12, "bold"),
                fg=fg, bg=bg).pack(anchor='w', pady=(0, 10))
        
        ModernCheckbox(options_frame, "Run in Headless Mode", self.browser_headless).pack(anchor='w', pady=2)

    def create_advanced_tab(self):
        """Create the advanced settings tab"""
        advanced_frame = tk.Frame(self.notebook, bg=self.get_color('bg'))
        self.notebook.add(advanced_frame, text="⚙️ Advanced")
        
        # Scrollable content
        canvas = tk.Canvas(advanced_frame, bg=self.get_color('bg'), highlightthickness=0)
        scrollbar = ttk.Scrollbar(advanced_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.get_color('bg'))
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Content
        content_frame = tk.Frame(scrollable_frame, bg=self.get_color('bg'))
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        fg, bg = self.get_fg_bg()
        title = tk.Label(content_frame, text="Advanced Settings", 
                        font=("Segoe UI", 18, "bold"),
                        fg=fg, bg=bg)
        title.pack(anchor='w', pady=(0, 20))
        
        # General settings
        general_frame = tk.Frame(content_frame, bg=self.get_color('card_bg'), relief=tk.FLAT, bd=1)
        general_frame.pack(fill='x', pady=20, ipady=15, ipadx=15)
        
        fg, bg = self.get_fg_bg()
        tk.Label(general_frame, text="General Settings", 
                font=("Segoe UI", 12, "bold"),
                fg=fg, bg=bg).pack(anchor='w', pady=(0, 10))
        
        ModernCheckbox(general_frame, "Auto-Restart", self.auto_restart_var).pack(anchor='w', pady=2)
        ModernCheckbox(general_frame, "Enable Hotkey Control", self.hotkey_control_var).pack(anchor='w', pady=2)
        ModernCheckbox(general_frame, "Enable Notifications", self.notifications_enabled).pack(anchor='w', pady=2)
        ModernCheckbox(general_frame, "Minimize on Start", self.minimize_on_start_var).pack(anchor='w', pady=2)
        
        # Timeout settings
        timeout_frame = tk.Frame(content_frame, bg=self.get_color('card_bg'), relief=tk.FLAT, bd=1)
        timeout_frame.pack(fill='x', pady=20, ipady=15, ipadx=15)
        
        fg, bg = self.get_fg_bg()
        tk.Label(timeout_frame, text="Timeout Settings", 
                font=("Segoe UI", 12, "bold"),
                fg=fg, bg=bg).pack(anchor='w', pady=(0, 10))
        
        fg, bg = self.get_fg_bg()
        ModernEntry(timeout_frame, "Idle Timeout (minutes)", self.idle_timeout_var, width=8, fg=fg, bg=bg).pack(anchor='w', pady=5)
        
        # Pause settings
        pause_frame = tk.Frame(content_frame, bg=self.get_color('card_bg'), relief=tk.FLAT, bd=1)
        pause_frame.pack(fill='x', pady=20, ipady=15, ipadx=15)
        
        fg, bg = self.get_fg_bg()
        tk.Label(pause_frame, text="Pause Settings", 
                font=("Segoe UI", 12, "bold"),
                fg=fg, bg=bg).pack(anchor='w', pady=(0, 10))
        
        self.pause_after_activity_var = tk.IntVar(value=getattr(self.app, 'pause_after_activity', 3))
        fg, bg = self.get_fg_bg()
        ModernSlider(pause_frame, "Pause After Activity (seconds)", self.pause_after_activity_var, from_=1, to=30, resolution=1, is_float=False, fg=fg, bg=bg).pack(anchor='w', pady=5)
        
        # Action buttons
        btn_frame = tk.Frame(pause_frame, bg=self.get_color('card_bg'))
        btn_frame.pack(fill='x', pady=10)
        
        ModernButton(btn_frame, "Test Settings", self.test_pause_settings, "warning").pack(side=tk.LEFT, padx=(0, 10))
        ModernButton(btn_frame, "Apply Settings", self.apply_pause_settings, "success").pack(side=tk.LEFT)
        
        # Config management
        config_frame = tk.Frame(content_frame, bg=self.get_color('card_bg'), relief=tk.FLAT, bd=1)
        config_frame.pack(fill='x', pady=20, ipady=15, ipadx=15)
        
        fg, bg = self.get_fg_bg()
        tk.Label(config_frame, text="Configuration Management", 
                font=("Segoe UI", 12, "bold"),
                fg=fg, bg=bg).pack(anchor='w', pady=(0, 10))
        
        config_btn_frame = tk.Frame(config_frame, bg=self.get_color('card_bg'))
        config_btn_frame.pack(fill='x', pady=10)
        
        ModernButton(config_btn_frame, "Show Config", self.show_config, "secondary").pack(side=tk.LEFT, padx=(0, 10))
        ModernButton(config_btn_frame, "Save Config As...", self.save_config_as, "primary").pack(side=tk.LEFT)
        
        # Advanced Tab (with all options, including Pause After Activity and Test/Apply)
        advanced_tab = ttk.Frame(self.notebook)
        self.notebook.add(advanced_tab, text="⚙️ Advanced")
        advanced_card = ttk.Frame(advanced_tab, style="GlassyCard.TFrame")
        advanced_card.pack(fill='both', expand=True, padx=12, pady=12)
        tk.Label(advanced_card, text="Advanced & UI Settings", font=("Segoe UI", 13, "bold"), pady=6, fg="#007AFF", bg="#f7fafd").pack(anchor='w', padx=10, pady=(10,0))
        self.tray_enabled_var = tk.BooleanVar(value=getattr(self.app, 'tray_enabled', True))
        def on_tray_toggle():
            if not self.tray_enabled_var.get():
                from tkinter import messagebox
                messagebox.showwarning(
                    "Stealth Mode Enabled",
                    "You are about to hide the tray icon.\n\nTo restore the tray icon, press the ~ key three times quickly.\n\nIf you close or minimize the main window, you will need to use this hotkey to bring the tray icon back."
                )
            self.app.tray_enabled = self.tray_enabled_var.get()
            if hasattr(self.app, 'system_tray'):
                if self.tray_enabled_var.get():
                    self.app.system_tray.tray_enabled = True
                    self.app.system_tray.setup_system_tray()
                else:
                    self.app.system_tray.tray_enabled = False
                    self.app.system_tray.hide_tray_icon()
        ttk.Checkbutton(advanced_card, text="Show Tray Icon (stealth mode)", variable=self.tray_enabled_var, command=on_tray_toggle).pack(anchor='w', padx=20, pady=2)

        # Simplified tray hotkey logic: ~ once hides, ~ twice quickly restores
        import keyboard
        import time
        self._tilde_press_times = []
        def tilde_press_handler(e):
            now = time.time()
            self._tilde_press_times = [t for t in self._tilde_press_times if now - t < 1]
            self._tilde_press_times.append(now)
            if len(self._tilde_press_times) == 1:
                # Hide tray icon
                self.tray_enabled_var.set(False)
                self.app.tray_enabled = False
                if hasattr(self.app, 'system_tray'):
                    self.app.system_tray.tray_enabled = False
                    self.app.system_tray.hide_tray_icon()
            elif len(self._tilde_press_times) == 2:
                # Restore tray icon
                self.tray_enabled_var.set(True)
                self.app.tray_enabled = True
                if hasattr(self.app, 'system_tray'):
                    self.app.system_tray.tray_enabled = True
                    if not getattr(self.app.system_tray, 'icon', None):
                        self.app.system_tray.setup_system_tray()
                self._tilde_press_times = []
        keyboard.on_press_key('`', tilde_press_handler, suppress=False)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_log_tab(self):
        """Create the log tab"""
        log_frame = tk.Frame(self.notebook, bg=self.get_color('bg'))
        self.notebook.add(log_frame, text="📝 Log")
        
        content_frame = tk.Frame(log_frame, bg=self.get_color('bg'))
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(content_frame, bg=self.get_color('bg'))
        header_frame.pack(fill='x', pady=(0, 10))
        
        fg, bg = self.get_fg_bg()
        tk.Label(header_frame, text="Activity Log", 
                font=("Segoe UI", 18, "bold"),
                fg=fg, bg=bg).pack(side=tk.LEFT)
        
        # Log buttons
        ModernButton(header_frame, "Refresh", self.refresh_log, "primary").pack(side=tk.RIGHT, padx=(10, 0))
        ModernButton(header_frame, "Clear", self.clear_log, "danger").pack(side=tk.RIGHT)
        
        # Log text area
        log_container = tk.Frame(content_frame, bg=self.get_color('card_bg'), relief=tk.FLAT, bd=1)
        log_container.pack(fill='both', expand=True, pady=10)
        
        fg, bg = self.get_fg_bg()
        self.log_text = tk.Text(
            log_container, height=15, state='normal', wrap='word',
            bg=bg, fg=fg,
            insertbackground=self.get_color('primary'),
            font=("Consolas", 10), relief=tk.FLAT, borderwidth=0
        )
        
        log_scrollbar = ttk.Scrollbar(log_container, command=self.log_text.yview)
        self.log_text['yscrollcommand'] = log_scrollbar.set
        
        self.log_text.pack(side=tk.LEFT, fill='both', expand=True, padx=10, pady=10)
        log_scrollbar.pack(side=tk.RIGHT, fill='y', pady=10)
        
        self.app.update_log_display()

    def create_footer(self, parent):
        """Create the footer section"""
        footer_frame = tk.Frame(parent, bg=self.get_color('card_bg'), relief=tk.FLAT, bd=0)
        footer_frame.pack(fill='x', pady=(20, 0))
        
        # Footer content
        footer_content = tk.Frame(footer_frame, bg=self.get_color('card_bg'))
        footer_content.pack(padx=20, pady=15)
        
        # Version and status info
        fg, bg = self.get_fg_bg()
        version_label = tk.Label(
            footer_content, text="Android Studio v1.0", 
            font=("Segoe UI", 9),
            fg=fg, bg=bg
        )
        version_label.pack(side=tk.LEFT)
        
        # Quick stats
        fg, bg = self.get_fg_bg()
        stats_label = tk.Label(
            footer_content, text="Ready", 
            font=("Segoe UI", 9),
            fg=fg, bg=bg
        )
        stats_label.pack(side=tk.RIGHT)

