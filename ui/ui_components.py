import tkinter as tk
from tkinter import ttk, colorchooser
import threading
from typing import Optional, Callable, Any
import logging
import random
import time
import os
import json
from .ui_styles import UIStyleManager
from logic.resources import get_resource_usage

class ModernTooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show)
        self.widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=self.text, background="#1F2937", foreground="white", 
                         relief="flat", borderwidth=0, padx=10, pady=5, font=("Segoe UI", 9))
        label.pack()

    def hide(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class ModernCheckbox(tk.Frame):
    def __init__(self, master, text, variable, **kwargs):
        bg = kwargs.get('bg', master.cget('bg'))
        super().__init__(master, bg=bg)
        self.variable = variable
        
        # Custom checkbox look (simplified as a label + click)
        self.indicator = tk.Label(self, text="✔" if variable.get() else " ", 
                                 font=("Segoe UI", 10, "bold"), width=2, height=1,
                                 bg="#3B82F6" if variable.get() else "#374151",
                                 fg="white", relief=tk.FLAT)
        self.indicator.pack(side=tk.LEFT, padx=(0, 10))
        
        self.label = tk.Label(self, text=text, font=("Segoe UI", 10), 
                             fg=kwargs.get('fg', '#F3F4F6'), bg=bg)
        self.label.pack(side=tk.LEFT)
        
        for widget in (self.indicator, self.label):
            widget.bind("<Button-1>", self.toggle)
            widget.bind("<Enter>", lambda e: self.on_enter())
            widget.bind("<Leave>", lambda e: self.on_leave())

    def toggle(self, event=None):
        new_val = not self.variable.get()
        self.variable.set(new_val)
        self.update_look()

    def update_look(self):
        self.indicator.config(text="✔" if self.variable.get() else " ",
                             bg="#3B82F6" if self.variable.get() else "#374151")

    def on_enter(self):
        self.label.config(fg="#60A5FA")

    def on_leave(self):
        self.label.config(fg="#F3F4F6")

class ModernButton(tk.Button):
    def __init__(self, master, text, command=None, style="primary", **kwargs):
        self.style = style
        self.colors = {
            "primary": {"bg": "#3B82F6", "fg": "#FFFFFF", "hover": "#2563EB"},
            "secondary": {"bg": "#374151", "fg": "#F3F4F6", "hover": "#4B5563"},
            "success": {"bg": "#10B981", "fg": "#FFFFFF", "hover": "#059669"},
            "danger": {"bg": "#EF4444", "fg": "#FFFFFF", "hover": "#DC2626"},
            "ghost": {"bg": "transparent", "fg": "#9CA3AF", "hover": "#374151"}
        }
        c = self.colors.get(style, self.colors["primary"])
        
        kwargs.pop('bg', None)
        kwargs.pop('fg', None)
        
        super().__init__(
            master, text=text, command=command,
            font=("Segoe UI", 9, "bold"),
            bg=c["bg"] if c["bg"] != "transparent" else master.cget("bg"),
            fg=c["fg"], relief=tk.FLAT, borderwidth=0,
            padx=15, pady=8, cursor="hand2", **kwargs
        )
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        c = self.colors.get(self.style, self.colors["primary"])
        self.config(bg=c["hover"])

    def on_leave(self, e):
        c = self.colors.get(self.style, self.colors["primary"])
        self.config(bg=c["bg"] if c["bg"] != "transparent" else self.master.cget("bg"))

class SidebarButton(tk.Frame):
    def __init__(self, master, text, icon, command, active_color="#3B82F6", **kwargs):
        super().__init__(master, bg=master.cget("bg"), pady=2)
        self.command = command
        self.is_active = False
        self.active_color = active_color
        
        self.indicator = tk.Frame(self, width=4, bg=master.cget("bg"))
        self.indicator.pack(side=tk.LEFT, fill='y')
        
        self.content = tk.Frame(self, bg=master.cget("bg"), padx=12, pady=6)
        self.content.pack(side=tk.LEFT, fill='x', expand=True)
        
        self.icon_label = tk.Label(self.content, text=icon, font=("Segoe UI", 12), 
                                  fg="#9CA3AF", bg=master.cget("bg"))
        self.icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        self.text_label = tk.Label(self.content, text=text, font=("Segoe UI", 10, "bold"), 
                                  fg="#9CA3AF", bg=master.cget("bg"))
        self.text_label.pack(side=tk.LEFT)
        
        for w in (self, self.content, self.icon_label, self.text_label):
            w.bind("<Button-1>", lambda e: self.command())
            w.bind("<Enter>", lambda e: self.on_enter())
            w.bind("<Leave>", lambda e: self.on_leave())

    def on_enter(self):
        if not self.is_active:
            self.content.config(bg="#1F2937")
            self.icon_label.config(bg="#1F2937", fg="#F3F4F6")
            self.text_label.config(bg="#1F2937", fg="#F3F4F6")

    def on_leave(self):
        if not self.is_active:
            self.content.config(bg=self.master.cget("bg"))
            self.icon_label.config(bg=self.master.cget("bg"), fg="#9CA3AF")
            self.text_label.config(bg=self.master.cget("bg"), fg="#9CA3AF")

    def set_active(self, active):
        self.is_active = active
        bg = "#1F2937" if active else self.master.cget("bg")
        fg = "#F3F4F6" if active else "#9CA3AF"
        self.indicator.config(bg=self.active_color if active else self.master.cget("bg"))
        self.content.config(bg=bg)
        self.icon_label.config(bg=bg, fg=self.active_color if active else fg)
        self.text_label.config(bg=bg, fg=fg)

class ModernSlider(tk.Frame):
    def __init__(self, master, label, variable, from_, to, is_float=False, **kwargs):
        super().__init__(master, bg=master.cget("bg"))
        
        header = tk.Frame(self, bg=master.cget("bg"))
        header.pack(fill='x')
        
        tk.Label(header, text=label, font=("Segoe UI", 9), fg="#9CA3AF", bg=master.cget("bg")).pack(side=tk.LEFT)
        self.val_label = tk.Label(header, text="", font=("Segoe UI", 9, "bold"), fg="#3B82F6", bg=master.cget("bg"))
        self.val_label.pack(side=tk.RIGHT)
        
        style = ttk.Style()
        style.configure("Modern.Horizontal.TScale", background=master.cget("bg"))
        
        self.scale = ttk.Scale(self, variable=variable, from_=from_, to=to, 
                              orient=tk.HORIZONTAL, style="Modern.Horizontal.TScale")
        self.scale.pack(fill='x', pady=(5, 0))
        
        def update(*args):
            v = variable.get()
            self.val_label.config(text=f"{v:.1f}" if is_float else f"{int(v)}")
        
        variable.trace_add("write", update)
        update()

class UIComponents:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.style_manager = UIStyleManager()
        self.is_dark_mode = True # Force Dark Mode for "Stunning" look
        self.colors = self.style_manager.get_theme('dark')
        
        # Cleanup previous UI if any
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.init_variables()
        self.setup_ui()

    def apply_theme(self):
        """No-op for forced dark theme, but kept for compatibility"""
        pass

    def update_log_display(self):
        if hasattr(self, 'log_text') and self.log_text:
            try:
                self.log_text.config(state='normal')
                if os.path.exists("anoid.log"):
                    with open("anoid.log", "r") as f:
                        lines = f.readlines()[-50:] # Last 50 lines
                        self.log_text.delete('1.0', tk.END)
                        self.log_text.insert(tk.END, "".join(lines))
                self.log_text.config(state='disabled')
                self.log_text.see(tk.END)
            except Exception:
                pass

    def init_variables(self):
        m = self.app.config.get('mouse', {})
        self.mouse_enabled = tk.BooleanVar(value=m.get('enabled', True))
        self.mouse_movements = tk.IntVar(value=m.get('movements', 5))
        self.mouse_min_duration = tk.DoubleVar(value=m.get('min_duration', 0.5))
        self.mouse_max_duration = tk.DoubleVar(value=m.get('max_duration', 2.0))
        
        k = self.app.config.get('keyboard', {})
        self.keyboard_enabled = tk.BooleanVar(value=k.get('enabled', True))
        self.dart_enabled = tk.BooleanVar(value=k.get('dart_enabled', False))
        self.keyboard_actions = tk.IntVar(value=k.get('actions', 3))
        
        s = self.app.config.get('schedule', {})
        self.schedule_enabled = tk.BooleanVar(value=s.get('enabled', False))
        self.schedule_start = tk.StringVar(value=s.get('start_time', '09:00'))
        self.schedule_end = tk.StringVar(value=s.get('end_time', '17:00'))
        
        self.process_cleaner_enabled = tk.BooleanVar(value=self.app.config.get('ui', {}).get('process_cleaner_enabled', False))

    def setup_ui(self):
        self.root.configure(bg="#111827")
        
        # Main Container
        main = tk.Frame(self.root, bg="#111827")
        main.pack(fill='both', expand=True)
        
        # Sidebar
        self.sidebar = tk.Frame(main, bg="#0F172A", width=150) # Narrower
        self.sidebar.pack(side=tk.LEFT, fill='y')
        self.sidebar.pack_propagate(False)
        
        # Logo
        logo_area = tk.Frame(self.sidebar, bg="#0F172A", pady=20) # Less padding
        logo_area.pack(fill='x')
        tk.Label(logo_area, text="Anoid", font=("Segoe UI", 16, "bold"), 
                 fg="#3B82F6", bg="#0F172A").pack()
        tk.Label(logo_area, text="V1.0 PRO", font=("Segoe UI", 7, "bold"), 
                 fg="#4B5563", bg="#0F172A").pack()
        
        # Nav Buttons
        self.nav_btns = {}
        items = [("Mouse", "🖱️"), ("Keyboard", "⌨️"), ("Advanced", "⚙️"), ("Log", "📝")]
        for name, icon in items:
            btn = SidebarButton(self.sidebar, name, icon, lambda n=name: self.show_page(n))
            btn.pack(fill='x')
            self.nav_btns[name] = btn
            
        # Content Area
        self.content = tk.Frame(main, bg="#111827", padx=25, pady=20)
        self.content.pack(side=tk.LEFT, fill='both', expand=True)
        
        # Top Bar (Inside Content)
        top_bar = tk.Frame(self.content, bg="#111827")
        top_bar.pack(fill='x', pady=(0, 20))
        
        self.title_label = tk.Label(top_bar, text="Mouse Settings", font=("Segoe UI", 16, "bold"), 
                                   fg="#F3F4F6", bg="#111827")
        self.title_label.pack(side=tk.LEFT)
        
        btn_group = tk.Frame(top_bar, bg="#111827")
        btn_group.pack(side=tk.RIGHT)
        
        self.status_dot = tk.Label(btn_group, text="● Ready", font=("Segoe UI", 9, "bold"), 
                                  fg="#10B981", bg="#111827", padx=10)
        self.status_dot.pack(side=tk.LEFT)
        
        ModernButton(btn_group, "▶ Start", self.app.start_simulation, "success").pack(side=tk.LEFT, padx=3)
        ModernButton(btn_group, "■ Stop", self.app.stop_simulation, "danger").pack(side=tk.LEFT, padx=3)
        
        # Page Frame
        self.page_frame = tk.Frame(self.content, bg="#111827")
        self.page_frame.pack(fill='both', expand=True)
        
        self.pages = {}
        self.create_pages()
        self.show_page("Mouse")

    def create_pages(self):
        self.create_mouse_page()
        self.create_keyboard_page()
        self.create_advanced_page()
        self.create_log_page()

    def show_page(self, name):
        self.title_label.config(text=f"{name} Settings" if name != "Log" else "Activity Log")
        for p in self.pages.values(): p.pack_forget()
        for n, b in self.nav_btns.items(): b.set_active(n == name)
        self.pages[name].pack(fill='both', expand=True)

    def create_card(self, parent, title=None):
        card = tk.Frame(parent, bg="#1F2937", padx=20, pady=20, highlightthickness=1, 
                        highlightbackground="#374151")
        card.pack(fill='x', pady=(0, 15))
        if title:
            tk.Label(card, text=title, font=("Segoe UI", 10, "bold"), 
                     fg="#9CA3AF", bg="#1F2937").pack(anchor='w', pady=(0, 15))
        return card

    def create_mouse_page(self):
        p = tk.Frame(self.page_frame, bg="#111827")
        self.pages["Mouse"] = p
        
        c1 = self.create_card(p)
        ModernCheckbox(c1, "Enable Mouse Activity Simulation", self.mouse_enabled, bg="#1F2937").pack(anchor='w')
        
        c2 = self.create_card(p, "MOVEMENT PARAMETERS")
        ModernSlider(c2, "Movements per Session", self.mouse_movements, 1, 30).pack(fill='x', pady=10)
        
        row = tk.Frame(c2, bg="#1F2937")
        row.pack(fill='x', pady=10)
        ModernSlider(row, "Min Duration (s)", self.mouse_min_duration, 0.1, 5.0, True).pack(side=tk.LEFT, fill='x', expand=True, padx=(0, 15))
        ModernSlider(row, "Max Duration (s)", self.mouse_max_duration, 0.5, 10.0, True).pack(side=tk.LEFT, fill='x', expand=True)

    def create_keyboard_page(self):
        p = tk.Frame(self.page_frame, bg="#111827")
        self.pages["Keyboard"] = p
        
        c1 = self.create_card(p)
        ModernCheckbox(c1, "Enable Keyboard Activity Simulation", self.keyboard_enabled, bg="#1F2937").pack(anchor='w')
        ModernCheckbox(c1, "Enable Dart Code Snippets", self.dart_enabled, bg="#1F2937").pack(anchor='w', pady=(10, 0))
        
        c2 = self.create_card(p, "TYPING BEHAVIOR")
        ModernSlider(c2, "Actions per Cycle", self.keyboard_actions, 1, 20).pack(fill='x')

    def create_advanced_page(self):
        p = tk.Frame(self.page_frame, bg="#111827")
        self.pages["Advanced"] = p
        
        c1 = self.create_card(p, "SYSTEM OPTIMIZER")
        ModernCheckbox(c1, "Enable Process Cleaner (Auto-kill distractions)", self.process_cleaner_enabled, bg="#1F2937").pack(anchor='w')
        
        c2 = self.create_card(p, "WORK SCHEDULE")
        ModernCheckbox(c2, "Enable Scheduled Activity", self.schedule_enabled, bg="#1F2937").pack(anchor='w', pady=(0, 15))
        
        row = tk.Frame(c2, bg="#1F2937")
        row.pack(fill='x')
        
        entry_f1 = tk.Frame(row, bg="#1F2937")
        entry_f1.pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(entry_f1, text="Start Time", font=("Segoe UI", 9), fg="#9CA3AF", bg="#1F2937").pack(anchor='w')
        tk.Entry(entry_f1, textvariable=self.schedule_start, font=("Segoe UI", 10), width=10, 
                 bg="#374151", fg="white", relief=tk.FLAT, insertbackground="white").pack(pady=5)
        
        entry_f2 = tk.Frame(row, bg="#1F2937")
        entry_f2.pack(side=tk.LEFT)
        tk.Label(entry_f2, text="End Time", font=("Segoe UI", 9), fg="#9CA3AF", bg="#1F2937").pack(anchor='w')
        tk.Entry(entry_f2, textvariable=self.schedule_end, font=("Segoe UI", 10), width=10, 
                 bg="#374151", fg="white", relief=tk.FLAT, insertbackground="white").pack(pady=5)
        
        ModernButton(p, "Apply All Changes", self.app.apply_changes, "success").pack(fill='x', pady=10)

    def create_log_page(self):
        p = tk.Frame(self.page_frame, bg="#111827")
        self.pages["Log"] = p
        
        header = tk.Frame(p, bg="#111827")
        header.pack(fill='x', pady=(0, 10))
        ModernButton(header, "Clear History", self.clear_log, "danger").pack(side=tk.RIGHT)
        
        log_card = tk.Frame(p, bg="#0F172A", padx=10, pady=10, highlightthickness=1, highlightbackground="#374151")
        log_card.pack(fill='both', expand=True)
        
        self.log_text = tk.Text(log_card, bg="#0F172A", fg="#9CA3AF", font=("Consolas", 9), 
                                relief=tk.FLAT, state='disabled', borderwidth=0)
        self.log_text.pack(fill='both', expand=True)
        self.app.update_log_display()

    def clear_log(self):
        if os.path.exists("anoid.log"):
            with open("anoid.log", "w") as f: f.write("")
        self.app.update_log_display()

    def get_color(self, name): return self.colors.get(name, "#000000")
    def toggle_dark_mode(self): pass # Fixed on Dark PRO theme
