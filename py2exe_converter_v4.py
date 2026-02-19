import tkinter as tk
from tkinter import filedialog, messagebox, ttk, font as tkfont
import os
import subprocess
import sys
import threading
from PIL import Image, ImageTk, ImageDraw
import json
import weakref
from collections import OrderedDict
from pathlib import Path
from datetime import datetime
import math
import platform
import queue
import weakref

class Tooltip:
    """Enhanced tooltip for tkinter widgets."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                        background="#2d2d2d", foreground="#ffffff",
                        relief=tk.SOLID, borderwidth=1,
                        font=("Segoe UI", "9", "normal"), padx=5, pady=2)
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

# EMBEDDED DOCS SUPPORT - Added for standalone executable
try:
    from embedded_docs import show_embedded_help
    EMBEDDED_DOCS_AVAILABLE = True
except ImportError:
    EMBEDDED_DOCS_AVAILABLE = False

class ModernPy2ExeConverter:
    """Modern Python to EXE Converter with enhanced GUI and icon management."""

    # Performance Optimization: Pre-calculate unit circle vertices for shapes to avoid
    # redundant trigonometric calculations during mask generation.
    HEX_VERTICES = [(math.cos(math.radians(60 * i)), math.sin(math.radians(60 * i))) for i in range(6)]
    STAR_VERTICES = [((1.0 if i % 2 == 0 else 0.4) * math.cos(math.radians(36 * i - 90)),
                      (1.0 if i % 2 == 0 else 0.4) * math.sin(math.radians(36 * i - 90)))
                     for i in range(10)]

    def __init__(self):
        """Initialize the main application window with modern styling."""
        self.root = tk.Tk()
        self.root.title("Modern Python to EXE Converter v4.0")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)

        # Modern color scheme with transparency support
        # This will be replaced by theme system
        self.setup_theme_system()

        # Configure root styling with color scheme
        self.root.configure(bg=self.colors['bg'])

        # Set window transparency (Windows only)
        try:
            self.root.wm_attributes('-alpha', 0.95)  # 95% opacity
        except:
            pass  # Fallback for systems that don't support transparency

        # Initialize variables
        self.selected_icon = tk.StringVar()
        self.conversion_settings = {}
        self.last_created_icon = None  # Track last created icon for auto-selection

        # Initialize thread-safe log queue
        self.log_queue = queue.Queue()
        self._process_log_queue()

        # Performance Optimization: Use WeakKeyDictionary for mousewheel scroll targets
        # to ensure destroyed widgets can be garbage collected from the cache.
        self._scroll_target_cache = weakref.WeakKeyDictionary()

        # Performance Optimization: Use OrderedDict for LRU caches to bound memory usage
        self.shaped_icons_cache = OrderedDict()
        self._mask_cache = OrderedDict()
        self._pyinstaller_version = None


        # Icon shape options (all with rounded corners)
        self.icon_shapes = {
            'square': 'Square with Rounded Corners',
            'circle': 'Circle',
            'triangle': 'Triangle',
            'hexagon': 'Hexagon',
            'star': 'Star',
            'diamond': 'Diamond'
        }

        # Create the GUI
        self.setup_styles()
        self.create_notebook()
        self.create_info_tab()
        self.create_converter_tab()
        self.create_icon_manager_tab()
        self.create_settings_tab()

        # Apply default settings
        self.apply_default_settings()
        # Apply modern styling effects
        self.apply_visual_effects()

        # Bind global keyboard shortcuts
        self.root.bind("<Control-o>", lambda e: self.select_files())
        self.root.bind("<Control-s>", lambda e: self.save_log())
        self.root.bind("<Control-Return>", lambda e: self.convert_to_exe())
        self.root.bind("<Control-q>", lambda e: self.root.quit())

    def create_tooltip(self, widget, text):
        """Helper to create a tooltip for a widget."""
        return Tooltip(widget, text)

    def _process_log_queue(self):
        """Process messages in the log queue with batched UI updates for better performance."""
        if not hasattr(self, 'output_text') or not self.output_text:
            self.root.after(100, self._process_log_queue)
            return

        messages_processed = 0
        batch_timestamp = None
        inserts = []

        try:
            # Optimization: Process up to 25 messages per tick to minimize UI thread overhead
            for _ in range(25):
                try:
                    message, level = self.log_queue.get_nowait()

                    # Performance Optimization: Calculate timestamp once per batch to avoid redundant calls
                    if messages_processed == 0:
                        batch_timestamp = datetime.now().strftime("%H:%M:%S")

                    # Performance Optimization: Collect all tag-text pairs for a single insert call
                    # This reduces IPC overhead between Python and the Tcl interpreter
                    inserts.extend([f"[{batch_timestamp}] ", "timestamp", f"{message}\n", level])
                    messages_processed += 1
                except queue.Empty:
                    break

            if inserts:
                self.output_text.config(state=tk.NORMAL)
                self.output_text.insert(tk.END, *inserts)
        finally:
            if messages_processed > 0:
                # Batch UI updates: Scroll and disable once per batch
                self.output_text.see(tk.END)
                self.output_text.config(state=tk.DISABLED)

            # Schedule next check
            self.root.after(100, self._process_log_queue)

    def _do_write_log(self, message, level):
        """Actually write to the log widget. Should only be called from the main UI thread."""
        # Note: Most logging now goes through the batched _process_log_queue
        if not hasattr(self, 'output_text') or not self.output_text:
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.output_text.insert(tk.END, f"{message}\n", level)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def setup_theme_system(self):
        """Initialize the theme and color system."""
        # Default directories (Desktop)
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

        # Default settings with theme support
        self.default_settings = {
            'default_output_dir': desktop_path,
            'default_icon_output_dir': desktop_path,
            'auto_select_created_icons': True,
            'show_icon_notifications': True,
            'window_transparency': 0.95,
            'theme': 'dark',
            'font_size': 10,
            'corner_radius': 10,
            'custom_theme': {
                'name': 'Custom',
                'bg': '#0f172a',
                'surface': '#111827',
                'card': '#1f2937',
                'border': '#334155',
                'fg': '#f8fafc',
                'accent': '#38bdf8',
                'accent_hover': '#0ea5e9',
                'success': '#22c55e',
                'warning': '#f59e0b',
                'error': '#ef4444'
            }
        }

        # Available themes
        self.available_themes = {
            'dark': {
                'name': 'Dark',
                'bg': '#0f172a',
                'surface': '#111827',
                'card': '#1f2937',
                'border': '#334155',
                'fg': '#f8fafc',
                'accent': '#38bdf8',
                'accent_hover': '#0ea5e9',
                'success': '#22c55e',
                'warning': '#f59e0b',
                'error': '#ef4444'
            },
            'light': {
                'name': 'Light',
                'bg': '#f8fafc',
                'surface': '#ffffff',
                'card': '#f1f5f9',
                'border': '#e2e8f0',
                'fg': '#0f172a',
                'accent': '#2563eb',
                'accent_hover': '#1d4ed8',
                'success': '#16a34a',
                'warning': '#d97706',
                'error': '#dc2626'
            },
            'blue': {
                'name': 'Ocean Blue',
                'bg': '#0f172a',
                'surface': '#122447',
                'card': '#1d335a',
                'border': '#2b4b76',
                'fg': '#e0f2fe',
                'accent': '#38bdf8',
                'accent_hover': '#0ea5e9',
                'success': '#22c55e',
                'warning': '#f59e0b',
                'error': '#f87171'
            },
            'green': {
                'name': 'Forest Green',
                'bg': '#0f172a',
                'surface': '#0f2f2a',
                'card': '#15403a',
                'border': '#1f5a52',
                'fg': '#ecfdf5',
                'accent': '#34d399',
                'accent_hover': '#10b981',
                'success': '#22c55e',
                'warning': '#fbbf24',
                'error': '#fb7185'
            },
            'purple': {
                'name': 'Royal Purple',
                'bg': '#0f172a',
                'surface': '#24153d',
                'card': '#2f1b4f',
                'border': '#3b2363',
                'fg': '#f5f3ff',
                'accent': '#a78bfa',
                'accent_hover': '#8b5cf6',
                'success': '#22c55e',
                'warning': '#f59e0b',
                'error': '#f87171'
            },
            'custom': {
                'name': 'Custom',
                'bg': '#0f172a',
                'surface': '#111827',
                'card': '#1f2937',
                'border': '#334155',
                'fg': '#f8fafc',
                'accent': '#38bdf8',
                'accent_hover': '#0ea5e9',
                'success': '#22c55e',
                'warning': '#f59e0b',
                'error': '#ef4444'
            }
        }

        # Load user settings
        self.load_settings()

        # Initialize color scheme based on selected theme
        self.init_color_scheme()

    def load_settings(self):
        """Load user settings from config file."""
        try:
            config_path = os.path.join(os.path.expanduser("~"), ".py2exe_converter_config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    saved_settings = json.load(f)
                    # Update default settings with saved ones
                    self.default_settings.update(saved_settings)
        except Exception as e:
            print(f"Could not load settings: {e}")

    def save_settings(self):
        """Save current settings to config file."""
        try:
            config_path = os.path.join(os.path.expanduser("~"), ".py2exe_converter_config.json")
            with open(config_path, 'w') as f:
                json.dump(self.default_settings, f, indent=2)
            if hasattr(self, 'log_output'):
                self.log_output("Settings saved successfully", "success")
        except Exception as e:
            if hasattr(self, 'log_output'):
                self.log_output(f"Could not save settings: {e}", "error")

    def init_color_scheme(self):
        """Initialize color scheme based on selected theme."""
        current_theme = self.default_settings.get('theme', 'dark')

        if current_theme == 'custom':
            # Use custom theme colors
            self.colors = self.default_settings['custom_theme'].copy()
        else:
            # Use predefined theme
            self.colors = self.available_themes.get(current_theme, self.available_themes['dark']).copy()

        # Remove 'name' key if it exists
        if 'name' in self.colors:
            del self.colors['name']

    def apply_theme(self, theme_name):
        """Apply a new theme to the application."""
        if theme_name in self.available_themes or theme_name == 'custom':
            self.default_settings['theme'] = theme_name
            self.init_color_scheme()

            # Update root window background
            self.root.configure(bg=self.colors['bg'])

            # Recreate styles with new colors
            self.setup_styles()

            # Apply transparency
            try:
                alpha = self.default_settings.get('window_transparency', 0.95)
                self.root.wm_attributes('-alpha', alpha)
            except:
                pass

            # Update all notebook tab styles
            if hasattr(self, 'notebook'):
                self.update_notebook_styles()

            # Update log tags for new theme colors
            self._setup_log_tags()

            # Log theme change
            if hasattr(self, 'log_output'):
                theme_display_name = self.available_themes.get(theme_name, {}).get('name', theme_name.title())
                self.log_output(f"Applied {theme_display_name} theme", "success")

    def update_notebook_styles(self):
        """Update notebook tab styles after theme change."""
        style = ttk.Style()
        style.configure('TNotebook',
                       background=self.colors['bg'])
        style.configure('TNotebook.Tab',
                       background=self.colors['card'],
                       foreground=self.colors['fg'])
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['accent']),
                            ('active', self.colors['accent_hover'])],
                 foreground=[('selected', 'white'),
                            ('active', 'white')])

    def update_custom_theme_color(self, color_key, color_value):
        """Update a specific color in the custom theme."""
        if 'custom_theme' not in self.default_settings:
            self.default_settings['custom_theme'] = self.available_themes['custom'].copy()

        self.default_settings['custom_theme'][color_key] = color_value

        # If currently using custom theme, apply immediately
        if self.default_settings.get('theme') == 'custom':
            self.apply_theme('custom')

    def setup_styles(self):
        """Configure modern ttk styles with enhanced appearance."""
        style = ttk.Style()
        style.theme_use('clam')

        self.base_font_size = max(9, int(self.default_settings.get('font_size', 10)))
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=self.base_font_size)
        text_font = tkfont.nametofont("TkTextFont")
        text_font.configure(family="Segoe UI", size=self.base_font_size)
        fixed_font = tkfont.nametofont("TkFixedFont")
        fixed_font.configure(family="Cascadia Code", size=max(self.base_font_size - 1, 9))

        # Performance Optimization: Pre-calculate and cache font tuples to avoid redundant allocations
        self.font_normal = ("Segoe UI", self.base_font_size)
        self.font_semibold = ("Segoe UI Semibold", self.base_font_size)
        self.font_title = ("Segoe UI Semibold", self.base_font_size + 2)
        self.mono_font = (fixed_font.cget("family"), fixed_font.cget("size"))
        
        # Configure enhanced styles
        style.configure('TNotebook', 
                       background=self.colors['bg'],
                       tabposition='n')
        style.configure('TNotebook.Tab', 
                       background=self.colors['card'],
                       foreground=self.colors['fg'],
                       padding=[22, 10],
                       focuscolor='none',
                       borderwidth=0,
                       font=self.font_semibold)
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['accent']),
                            ('active', self.colors['accent_hover'])],
                 foreground=[('selected', 'white'),
                            ('active', 'white')])
        
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabelFrame', 
                       background=self.colors['surface'],
                       foreground=self.colors['fg'],
                       borderwidth=1,
                       relief='solid')
        style.configure('TLabelframe.Label',
                       background=self.colors['surface'],
                       foreground=self.colors['fg'],
                       font=self.font_semibold)
        style.configure('TLabel', 
                       background=self.colors['surface'],
                       foreground=self.colors['fg'],
                       font=self.font_normal)
        style.configure('TCombobox',
                       fieldbackground=self.colors['card'],
                       background=self.colors['surface'],
                       foreground=self.colors['fg'],
                       arrowcolor=self.colors['fg'])
        style.map('TCombobox',
                 fieldbackground=[('readonly', self.colors['card'])],
                 foreground=[('readonly', self.colors['fg'])],
                 background=[('readonly', self.colors['surface'])])
        style.configure('TScrollbar',
                       background=self.colors['surface'],
                       troughcolor=self.colors['bg'],
                       bordercolor=self.colors['bg'],
                       arrowcolor=self.colors['fg'])
        
        # Enhanced progressbar
        style.configure('TProgressbar',
                       background=self.colors['accent'],
                       troughcolor=self.colors['card'],
                       borderwidth=0,
                       lightcolor=self.colors['accent'],
                       darkcolor=self.colors['accent'])

        # Update cached button configurations
        self._update_button_config()

    def _update_button_config(self):
        """Pre-calculate and cache button styles and sizes to improve performance."""
        self.BUTTON_STYLES = {
            'default': {
                'bg': self.colors['card'],
                'hover': self.colors['surface'],
                'fg': self.colors['fg']
            },
            'primary': {
                'bg': self.colors['accent'],
                'hover': self.colors['accent_hover'],
                'fg': 'white'
            },
            'success': {
                'bg': self.colors['success'],
                'hover': '#16a34a',
                'fg': 'white'
            },
            'warning': {
                'bg': self.colors['warning'],
                'hover': '#d97706',
                'fg': 'white'
            },
            'danger': {
                'bg': self.colors['error'],
                'hover': '#dc2626',
                'fg': 'white'
            }
        }

        self.BUTTON_SIZES = {
            'normal': {'font': self.font_semibold, 'pady': 8, 'padx': 20},
            'large': {'font': self.font_title, 'pady': 12, 'padx': 30}
        }

    def apply_visual_effects(self):
        """Apply visual effects to enhance the modern appearance."""
        self.root.update_idletasks()

    def apply_default_settings(self):
        """Apply default settings to the GUI."""
        # Set default output directory
        if hasattr(self, 'output_entry') and self.default_settings['default_output_dir']:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, self.default_settings['default_output_dir'])

        # Set default icon search directory
        if hasattr(self, 'search_entry') and self.default_settings['default_icon_output_dir']:
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, self.default_settings['default_icon_output_dir'])

        # Apply transparency
        try:
            alpha = self.default_settings.get('window_transparency', 0.95)
            self.root.wm_attributes('-alpha', alpha)
        except:
            pass

    def create_notebook(self):
        """Create the main notebook widget for tabs."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=15, pady=15)

    def create_info_tab(self):
        """Create the info tab with application information and instructions."""
        # Main info frame
        self.info_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.info_frame, text="ℹ️ Info")

        # Create main container with scrollable canvas
        canvas = tk.Canvas(self.info_frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.info_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mouse wheel
        canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # App header section
        self.create_app_header(scrollable_frame)

        # Features section
        self.create_features_section(scrollable_frame)

        # Quick start section
        self.create_quick_start_section(scrollable_frame)

        # Tips and tricks section
        self.create_tips_section(scrollable_frame)

        # Version info section
        self.create_version_info_section(scrollable_frame)

    def create_app_header(self, parent):
        """Create the main application header with welcome message."""
        header_frame = ttk.LabelFrame(parent, text="🚀 Welcome to Modern Python to EXE Converter v4.0")
        header_frame.pack(fill='x', padx=15, pady=10)
        
        # Welcome message
        welcome_text = tk.Text(header_frame, height=4, bg=self.colors['card'], 
                              fg=self.colors['fg'], wrap=tk.WORD, 
                              borderwidth=0, highlightthickness=0,
                              font=('Segoe UI', self.base_font_size + 2))
        welcome_text.pack(fill='x', padx=15, pady=15)

        welcome_text.insert('1.0',
            "✨ Welcome to the enhanced Python to EXE converter! This modern application provides "
            "a comprehensive solution for converting your Python scripts to standalone executables "
            "with advanced features including shaped icon creation, automatic dependency detection, "
            "and desktop-default directories for easy access.")
        welcome_text.config(state='disabled')

    def create_features_section(self, parent):
        """Create the features showcase section."""
        features_frame = ttk.LabelFrame(parent, text="🌟 Key Features")
        features_frame.pack(fill='x', padx=15, pady=10)

        features_container = tk.Frame(features_frame, bg=self.colors['surface'])
        features_container.pack(fill='x', padx=15, pady=15)

        # Create feature cards in a grid
        features = [
            ("🎨", "Shaped Icon Creation", "Create beautiful icons with various shapes: circles, triangles, hexagons, stars, and more"),
            ("⚡", "One-Click Conversion", "Convert multiple Python files to executables with a single click"),
            ("🔧", "Advanced Options", "Full control over PyInstaller options including hidden imports and data files"),
            ("📁", "Smart Defaults", "Desktop-default output directories for easy access to your converted files"),
            ("🎯", "Auto Icon Selection", "Automatically select newly created icons for your conversions"),
            ("🌙", "Multiple Themes", "Choose from Dark, Light, Blue, Green, Purple themes or create custom colors"),
            ("📊", "Real-time Progress", "Live progress tracking with detailed logging and color-coded messages"),
            ("💾", "Settings Persistence", "Your preferences are saved and restored across sessions")
        ]

        for i, (emoji, title, description) in enumerate(features):
            row = i // 2
            col = i % 2

            feature_card = tk.Frame(features_container, bg=self.colors['card'],
                                   relief='flat', borderwidth=0,
                                   highlightthickness=1, highlightbackground=self.colors['border'])
            feature_card.grid(row=row, column=col, padx=10, pady=5, sticky='ew')

            # Configure grid weights
            features_container.grid_columnconfigure(col, weight=1)

            # Feature header
            header_frame = tk.Frame(feature_card, bg=self.colors['card'])
            header_frame.pack(fill='x', padx=10, pady=(10, 5))

            emoji_label = tk.Label(header_frame, text=emoji, 
                                  bg=self.colors['card'], fg=self.colors['fg'],
                                  font=('Segoe UI', self.base_font_size + 6))
            emoji_label.pack(side='left')

            title_label = tk.Label(header_frame, text=title,
                                  bg=self.colors['card'], fg=self.colors['accent'],
                                  font=('Segoe UI Semibold', self.base_font_size + 1))
            title_label.pack(side='left', padx=(10, 0))

            # Feature description
            desc_label = tk.Label(feature_card, text=description,
                                 bg=self.colors['card'], fg=self.colors['fg'],
                                 font=('Segoe UI', self.base_font_size), wraplength=250,
                                 justify='left')
            desc_label.pack(fill='x', padx=10, pady=(0, 10))

    def create_quick_start_section(self, parent):
        """Create the quick start guide section."""
        quickstart_frame = ttk.LabelFrame(parent, text="🚀 Quick Start Guide")
        quickstart_frame.pack(fill='x', padx=15, pady=10)

        steps_container = tk.Frame(quickstart_frame, bg=self.colors['surface'])
        steps_container.pack(fill='x', padx=15, pady=15)

        steps = [
            "1️⃣ Click 'Add Files' in the Converter tab to select your Python scripts",
            "2️⃣ Choose or create an icon in the Icon Manager tab (optional)",
            "3️⃣ Set your output directory or use the default Desktop location",
            "4️⃣ Configure conversion options (single file, no console, etc.)",
            "5️⃣ Click 'Convert to EXE' and watch the magic happen!",
            "🎉 Find your executable files in the output directory"
        ]

        for step in steps:
            step_frame = tk.Frame(steps_container, bg=self.colors['card'],
                                 relief='flat', borderwidth=0,
                                 highlightthickness=1, highlightbackground=self.colors['border'])
            step_frame.pack(fill='x', pady=2)
            
            step_label = tk.Label(step_frame, text=step,
                                 bg=self.colors['card'], fg=self.colors['fg'],
                                 font=('Segoe UI', self.base_font_size + 1), anchor='w')
            step_label.pack(fill='x', padx=15, pady=8)

    def create_tips_section(self, parent):
        """Create the tips and tricks section."""
        tips_frame = ttk.LabelFrame(parent, text="💡 Tips & Tricks")
        tips_frame.pack(fill='x', padx=15, pady=10)

        tips_container = tk.Frame(tips_frame, bg=self.colors['surface'])
        tips_container.pack(fill='x', padx=15, pady=15)
        
        tips = [
            "💡 Use 'Validate Settings' to check your configuration before conversion",
            "🎨 Try different icon shapes to make your application stand out",
            "⚙️ Customize themes in Settings to match your preferred color scheme",
            "📦 The application auto-detects most dependencies - only add hidden imports if needed",
            "🔍 Use the Icon Browser to find and preview existing icon files",
            "💾 Your settings are automatically saved and will be restored next time"
        ]

        for tip in tips:
            tip_frame = tk.Frame(tips_container, bg=self.colors['card'],
                                relief='flat', borderwidth=0,
                                highlightthickness=1, highlightbackground=self.colors['border'])
            tip_frame.pack(fill='x', pady=2)
            
            tip_label = tk.Label(tip_frame, text=tip,
                                bg=self.colors['card'], fg=self.colors['fg'],
                                font=('Segoe UI', self.base_font_size), anchor='w', wraplength=800)
            tip_label.pack(fill='x', padx=15, pady=8)

    def create_version_info_section(self, parent):
        """Create the version and system information section."""
        version_frame = ttk.LabelFrame(parent, text="📋 System Information")
        version_frame.pack(fill='x', padx=15, pady=10)

        info_container = tk.Frame(version_frame, bg=self.colors['surface'])
        info_container.pack(fill='x', padx=15, pady=15)

        # System information
        import platform
        system_info = [
            f"Application Version: Modern Python to EXE Converter v4.0",
            f"Python Version: {sys.version.split()[0]}",
            f"Operating System: {platform.system()} {platform.release()}",
            f"Architecture: {platform.architecture()[0]}",
            f"Current Working Directory: {os.getcwd()}",
            f"Default Output Directory: {self.default_settings.get('default_output_dir', 'Not set')}"
        ]

        for info in system_info:
            info_label = tk.Label(info_container, text=info,
                                 bg=self.colors['surface'], fg=self.colors['fg'],
                                 font=self.mono_font, anchor='w')
            info_label.pack(fill='x', pady=2)
        
        # Buttons frame
        buttons_frame = tk.Frame(info_container, bg=self.colors['surface'])
        buttons_frame.pack(fill='x', pady=(15, 0))

        # Check PyInstaller button
        def check_pyinstaller():
            if self._pyinstaller_version:
                messagebox.showinfo("PyInstaller Status",
                                   f"✅ PyInstaller is installed\nVersion: {self._pyinstaller_version}")
                return

            try:
                result = subprocess.run(["pyinstaller", "--version"],
                                      capture_output=True, text=True, check=True)
                self._pyinstaller_version = result.stdout.strip()
                messagebox.showinfo("PyInstaller Status",
                                   f"✅ PyInstaller is installed\nVersion: {self._pyinstaller_version}")
            except (FileNotFoundError, subprocess.CalledProcessError):
                result = messagebox.askyesno("PyInstaller Not Found",
                    "❌ PyInstaller is not installed or not found in PATH.\n\n"
                    "Would you like to install it now?")
                if result:
                    self.install_pyinstaller()

        self.create_modern_button(buttons_frame, "🔍 Check PyInstaller",
                                 check_pyinstaller, 'left', style='primary')

        def open_output_dir():
            output_dir = self.default_settings.get('default_output_dir')
            if output_dir and os.path.exists(output_dir):
                os.startfile(output_dir)
            else:
                messagebox.showwarning("Directory Not Found",
                                     "Default output directory not found or not set.")

        self.create_modern_button(buttons_frame, "📁 Open Output Directory",
                                 open_output_dir, 'left', style='success')


        # Add Help menu with embedded documentation (if available)
        if EMBEDDED_DOCS_AVAILABLE:
            self.add_help_menu()

    def add_help_menu(self):
        """Add Help menu to the application."""
        try:
            # Create menu bar if it doesn't exist
            if not hasattr(self.root, 'menubar'):
                menubar = tk.Menu(self.root)
                self.root.config(menu=menubar)
                self.root.menubar = menubar
            else:
                menubar = self.root.menubar

            # Add Help menu
            help_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="📚 Help", menu=help_menu)

            help_menu.add_command(label="📖 User Guide & Documentation",
                                 command=show_embedded_help)
            help_menu.add_separator()
            help_menu.add_command(label="ℹ️ About",
                                 command=self.show_about_dialog)

        except Exception as e:
            # Fail silently if menu creation fails
            pass

    def show_about_dialog(self):
        """Show about dialog."""
        from tkinter import messagebox
        about_text = """Modern Python to EXE Converter v4.0

🚀 A comprehensive tool for converting Python scripts to executables

✨ Features:
• Modern dark theme interface
• Advanced icon manager with shapes
• Batch file conversion
• Real-time progress tracking
• Complete settings management
• Embedded documentation

📧 This standalone executable includes all documentation.
Use Help menu to access guides and export files."""

        messagebox.showinfo("About", about_text)

    def create_converter_tab(self):
        """Create the main converter tab with enhanced UI."""
        # Main converter frame
        self.converter_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.converter_frame, text="🔧 Converter")

        # Create main container with scrollable canvas
        canvas = tk.Canvas(self.converter_frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.converter_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Python files section
        self.create_files_section(scrollable_frame)

        # Output directory section
        self.create_output_section(scrollable_frame)

        # Options section
        self.create_options_section(scrollable_frame)

        # Conversion controls
        self.create_conversion_controls(scrollable_frame)

        # Output log
        self.create_output_log(scrollable_frame)

    def create_files_section(self, parent):
        """Create the Python files selection section."""
        files_frame = ttk.LabelFrame(parent, text="📁 Python Files to Convert")
        files_frame.pack(fill='x', padx=15, pady=10)

        # Files listbox with modern styling
        listbox_frame = tk.Frame(files_frame, bg=self.colors['surface'])
        listbox_frame.pack(fill='x', padx=15, pady=15)
        
        self.files_listbox = tk.Listbox(listbox_frame, 
                                       selectmode=tk.MULTIPLE,
                                       bg=self.colors['card'],
                                       fg=self.colors['fg'],
                                       selectbackground=self.colors['accent'],
                                       selectforeground='white',
                                       height=5,
                                       borderwidth=0,
                                       highlightthickness=1,
                                       highlightbackground=self.colors['border'],
                                       highlightcolor=self.colors['accent'],
                                       font=('Segoe UI', self.base_font_size))
        self.files_listbox.pack(side='left', fill='both', expand=True)

        files_scrollbar = ttk.Scrollbar(listbox_frame, orient='vertical')
        files_scrollbar.pack(side='right', fill='y')

        self.files_listbox.config(yscrollcommand=files_scrollbar.set)
        files_scrollbar.config(command=self.files_listbox.yview)

        # Buttons frame
        buttons_frame = tk.Frame(files_frame, bg=self.colors['surface'])
        buttons_frame.pack(fill='x', padx=15, pady=10)

        btn_add = self.create_modern_button(buttons_frame, "➕ Add Files",
                                 self.select_files, 'left', style='primary')
        self.create_tooltip(btn_add, "Select Python scripts to convert (Ctrl+O)")

        btn_remove = self.create_modern_button(buttons_frame, "➖ Remove Selected",
                                 lambda: self.remove_selected(self.files_listbox), 'left')
        self.create_tooltip(btn_remove, "Remove selected files from the list")

        btn_clear = self.create_modern_button(buttons_frame, "🗑️ Clear All",
                                 lambda: self.files_listbox.delete(0, tk.END), 'left', style='danger')
        self.create_tooltip(btn_clear, "Remove all files from the list")

        # Double-click to remove
        self.files_listbox.bind("<Double-1>", lambda e: self.remove_selected(self.files_listbox))

        # Right-click context menu
        self.files_context_menu = tk.Menu(self.root, tearoff=0,
                                        bg=self.colors['card'], fg=self.colors['fg'],
                                        activebackground=self.colors['accent'])
        self.files_context_menu.add_command(label="📁 Open File Location", command=self._open_file_location)
        self.files_context_menu.add_command(label="🗑️ Remove from List", command=lambda: self.remove_selected(self.files_listbox))

        self.files_listbox.bind("<Button-3>", self._show_context_menu)

    def _show_context_menu(self, event):
        """Show the context menu for the files listbox."""
        try:
            # Select the item under the mouse
            index = self.files_listbox.nearest(event.y)
            self.files_listbox.selection_clear(0, tk.END)
            self.files_listbox.selection_set(index)
            self.files_listbox.activate(index)
            self.files_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.files_context_menu.grab_release()

    def _open_file_location(self):
        """Open the location of the selected file in explorer."""
        selected = self.files_listbox.curselection()
        if selected:
            path = self.files_listbox.get(selected[0])
            if os.path.exists(path):
                folder = os.path.dirname(path)
                if platform.system() == 'Windows':
                    os.startfile(folder)
                elif platform.system() == 'Darwin':
                    subprocess.run(['open', folder])
                else:
                    subprocess.run(['xdg-open', folder])

    def create_output_section(self, parent):
        """Create the output directory selection section."""
        output_frame = ttk.LabelFrame(parent, text="📂 Output Directory")
        output_frame.pack(fill='x', padx=15, pady=10)

        dir_frame = tk.Frame(output_frame, bg=self.colors['surface'])
        dir_frame.pack(fill='x', padx=15, pady=15)
        
        self.output_entry = tk.Entry(dir_frame, 
                                    bg=self.colors['card'],
                                    fg=self.colors['fg'],
                                    insertbackground=self.colors['fg'],
                                    borderwidth=0,
                                    highlightthickness=1,
                                    highlightbackground=self.colors['border'],
                                    highlightcolor=self.colors['accent'],
                                    font=('Segoe UI', self.base_font_size + 1))
        self.output_entry.pack(side='left', fill='x', expand=True, padx=(0, 15))
        self._add_placeholder(self.output_entry, "Path to output directory...")

        btn_browse_out = self.create_modern_button(dir_frame, "📁 Browse",
                                 self.select_directory, 'right', style='primary')
        self.create_tooltip(btn_browse_out, "Choose where to save the executable")

    def create_options_section(self, parent):
        """Create the advanced options section."""
        options_frame = ttk.LabelFrame(parent, text="⚙️ Conversion Options")
        options_frame.pack(fill='x', padx=15, pady=10)

        # Basic options
        basic_frame = tk.Frame(options_frame, bg=self.colors['surface'])
        basic_frame.pack(fill='x', padx=15, pady=10)

        self.onefile_var = tk.BooleanVar(value=True)
        self.noconsole_var = tk.BooleanVar()
        self.debug_var = tk.BooleanVar()

        # Create checkboxes using pack manager with enhanced styling
        cb1 = self.create_modern_checkbox(basic_frame, "📦 Create single file", self.onefile_var)
        cb1.pack(side='left', padx=15)

        cb2 = self.create_modern_checkbox(basic_frame, "🚫 No console window", self.noconsole_var)
        cb2.pack(side='left', padx=15)

        cb3 = self.create_modern_checkbox(basic_frame, "🐛 Debug mode", self.debug_var)
        cb3.pack(side='left', padx=15)

        # Icon selection
        icon_frame = tk.Frame(options_frame, bg=self.colors['surface'])
        icon_frame.pack(fill='x', padx=15, pady=10)

        ttk.Label(icon_frame, text="🎨 Icon File (optional):").pack(side='left')

        self.icon_entry = tk.Entry(icon_frame,
                                  bg=self.colors['card'],
                                  fg=self.colors['fg'],
                                  insertbackground=self.colors['fg'],
                                  borderwidth=0,
                                  highlightthickness=1,
                                  highlightbackground=self.colors['border'],
                                  highlightcolor=self.colors['accent'],
                                  font=('Segoe UI', self.base_font_size + 1))
        self.icon_entry.pack(side='left', fill='x', expand=True, padx=15)
        self._add_placeholder(self.icon_entry, "Path to .ico file...")

        btn_browse_icon = self.create_modern_button(icon_frame, "🔍 Browse",
                                 self.select_icon_file, 'right', style='primary')
        self.create_tooltip(btn_browse_icon, "Choose a custom icon for the executable")

        # Hidden imports section (simplified - auto-detection handles most cases)
        self.create_hidden_imports_section(options_frame)

    def create_hidden_imports_section(self, parent):
        """Create the hidden imports management section."""
        hidden_frame = tk.Frame(parent, bg=self.colors['surface'])
        hidden_frame.pack(fill='x', padx=15, pady=10)
        
        # Info label
        info_label = tk.Label(hidden_frame,
                             text="📦 Hidden Imports (Only add if auto-detection fails):",
                             bg=self.colors['surface'],
                             fg=self.colors['fg'],
                             font=('Segoe UI', self.base_font_size))
        info_label.pack(anchor='w')
        
        # Helper text
        helper_text = tk.Label(hidden_frame,
                              text="💡 PyInstaller automatically detects most dependencies. Only add modules here if you encounter import errors.",
                              bg=self.colors['surface'],
                              fg=self.colors['border'],
                              font=('Segoe UI', self.base_font_size - 1),
                              wraplength=600)
        helper_text.pack(anchor='w', pady=(0, 5))
        
        hidden_container = tk.Frame(hidden_frame, bg=self.colors['surface'])
        hidden_container.pack(fill='x', pady=10)
        
        self.hidden_listbox = tk.Listbox(hidden_container,
                                        bg=self.colors['card'],
                                        fg=self.colors['fg'],
                                        selectbackground=self.colors['accent'],
                                        selectforeground='white',
                                        height=3,
                                        borderwidth=0,
                                        highlightthickness=1,
                                        highlightbackground=self.colors['border'],
                                        highlightcolor=self.colors['accent'],
                                        font=('Segoe UI', self.base_font_size))
        self.hidden_listbox.pack(side='left', fill='both', expand=True)

        hidden_scrollbar = ttk.Scrollbar(hidden_container, orient='vertical')
        hidden_scrollbar.pack(side='right', fill='y')

        self.hidden_listbox.config(yscrollcommand=hidden_scrollbar.set)
        hidden_scrollbar.config(command=self.hidden_listbox.yview)

        hidden_buttons = tk.Frame(hidden_frame, bg=self.colors['surface'])
        hidden_buttons.pack(fill='x', pady=10)

        btn_add_hidden = self.create_modern_button(hidden_buttons, "➕ Add Import",
                                 self.add_hidden_import, 'left', style='primary')
        self.create_tooltip(btn_add_hidden, "Manually add a missing dependency")

        btn_remove_hidden = self.create_modern_button(hidden_buttons, "➖ Remove Selected",
                                 lambda: self.remove_selected(self.hidden_listbox), 'left')
        self.create_tooltip(btn_remove_hidden, "Remove selected import from the list")

        # Double-click to remove
        self.hidden_listbox.bind("<Double-1>", lambda e: self.remove_selected(self.hidden_listbox))

    def create_conversion_controls(self, parent):
        """Create the conversion control buttons and progress bar."""
        controls_frame = ttk.LabelFrame(parent, text="🚀 Conversion Controls")
        controls_frame.pack(fill='x', padx=15, pady=10)

        # Convert button
        button_frame = tk.Frame(controls_frame, bg=self.colors['surface'])
        button_frame.pack(fill='x', padx=15, pady=15)

        self.convert_btn = self.create_modern_button(button_frame, "🔄 Convert to EXE",
                                                    self.convert_to_exe, 'left',
                                                    style='success', size='large')
        self.create_tooltip(self.convert_btn, "Start the conversion process (Ctrl+Enter)")

        self.validate_btn = self.create_modern_button(button_frame, "✅ Validate Settings",
                                                     self.validate_settings, 'left',
                                                     style='warning')
        self.create_tooltip(self.validate_btn, "Check if all settings are correct before conversion")

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(controls_frame,
                                           variable=self.progress_var,
                                           mode='determinate')
        self.progress_bar.pack(fill='x', padx=15, pady=10)

        # Status label
        self.status_label = tk.Label(controls_frame,
                                    text="Ready to convert",
                                    bg=self.colors['surface'],
                                    fg=self.colors['fg'],
                                    font=('Segoe UI', self.base_font_size + 1))
        self.status_label.pack(pady=10)

    def create_output_log(self, parent):
        """Create the output log section."""
        log_frame = ttk.LabelFrame(parent, text="📋 Conversion Log")
        log_frame.pack(fill='both', expand=True, padx=15, pady=10)

        # Log text widget with scrollbar
        log_container = tk.Frame(log_frame, bg=self.colors['surface'])
        log_container.pack(fill='both', expand=True, padx=15, pady=15)
        
        self.output_text = tk.Text(log_container,
                                  bg=self.colors['card'],
                                  fg=self.colors['fg'],
                                  insertbackground=self.colors['fg'],
                                  height=8,
                                  borderwidth=0,
                                  highlightthickness=1,
                                  highlightbackground=self.colors['border'],
                                  highlightcolor=self.colors['accent'],
                                  wrap=tk.WORD,
                                  state=tk.DISABLED,
                                  font=self.mono_font)
        self.output_text.pack(side='left', fill='both', expand=True)

        log_scrollbar = ttk.Scrollbar(log_container, orient='vertical')
        log_scrollbar.pack(side='right', fill='y')

        self.output_text.config(yscrollcommand=log_scrollbar.set)
        log_scrollbar.config(command=self.output_text.yview)

        # Log controls
        log_controls = tk.Frame(log_frame, bg=self.colors['surface'])
        log_controls.pack(fill='x', padx=15, pady=10)

        btn_clear_log = self.create_modern_button(log_controls, "🗑️ Clear Log",
                                 self.clear_log, 'left')
        self.create_tooltip(btn_clear_log, "Clear all messages from the log")

        btn_save_log = self.create_modern_button(log_controls, "💾 Save Log",
                                 self.save_log, 'left', style='primary')
        self.create_tooltip(btn_save_log, "Save the current log to a text file (Ctrl+S)")

        btn_copy_log = self.create_modern_button(log_controls, "📋 Copy Log",
                                 self.copy_log_to_clipboard, 'left')
        self.create_tooltip(btn_copy_log, "Copy all log text to clipboard")

        # Initialize log tags
        self._setup_log_tags()

        # Initial welcome message
        self.log_output("🎉 Welcome to Modern Python to EXE Converter v4.0", "info")
        self.log_output(f"Session started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "info")
        self.log_output("💡 New features: Desktop defaults, auto icon selection, settings tab, rounded icons", "info")

    # Continue with rest of methods in next part...

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling with cached target lookup for better performance."""
        delta = event.delta
        if platform.system() == 'Windows':
            scroll = -1 * (delta // 120)
        else:
            scroll = -1 * delta

        widget = event.widget

        # Check cache first to avoid repeated tree traversal
        if widget in self._scroll_target_cache:
            target = self._scroll_target_cache[widget]
            if target:
                try:
                    target.yview_scroll(scroll, "units")
                    return
                except (tk.TclError, AttributeError):
                    # Cache entry might be stale if widget was destroyed
                    del self._scroll_target_cache[widget]
            else:
                # We already know this widget has no scrollable parent
                return

        # Safely find and cache the parent scrollable widget
        curr = widget
        while curr:
            if hasattr(curr, 'yview_scroll'):
                self._scroll_target_cache[widget] = curr
                try:
                    curr.yview_scroll(scroll, "units")
                    return
                except tk.TclError:
                    pass
            curr = curr.master

        # Cache that no scrollable parent was found
        self._scroll_target_cache[widget] = None

    def _on_widget_enter(self, event):
        """Shared event handler for widget enter (hover) to avoid redundant closure allocations."""
        if hasattr(event.widget, '_hover_bg'):
            event.widget.configure(bg=event.widget._hover_bg)

    def _on_widget_leave(self, event):
        """Shared event handler for widget leave."""
        if hasattr(event.widget, '_normal_bg'):
            event.widget.configure(bg=event.widget._normal_bg)

    def _on_widget_focus_in(self, event):
        """Shared event handler for widget focus in."""
        if hasattr(event.widget, '_focus_bg'):
            event.widget.configure(highlightbackground=event.widget._focus_bg, highlightthickness=2)
        if hasattr(event.widget, '_focus_fg'):
            event.widget.configure(fg=event.widget._focus_fg)

    def _on_widget_focus_out(self, event):
        """Shared event handler for widget focus out."""
        if hasattr(event.widget, '_focus_out_bg'):
            event.widget.configure(highlightbackground=event.widget._focus_out_bg, highlightthickness=1)
        if hasattr(event.widget, '_normal_fg'):
            event.widget.configure(fg=event.widget._normal_fg)

    def _add_placeholder(self, entry, placeholder):
        """Add placeholder text to an entry widget."""
        def on_focus_in(e):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=self.colors['fg'])

        def on_focus_out(e):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg=self.colors['border'])

        entry.insert(0, placeholder)
        entry.config(fg=self.colors['border'])
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def copy_log_to_clipboard(self):
        """Copy log output to system clipboard."""
        try:
            log_content = self.output_text.get(1.0, tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(log_content)
            self.log_output("Log copied to clipboard", "success")
        except Exception as e:
            self.log_output(f"Failed to copy log: {e}", "error")

    def create_modern_button(self, parent, text, command, side, style='default', size='normal'):
        """Create a modern styled button using cached configurations for better performance."""
        # Performance Optimization: Use pre-calculated button styles and sizes
        style_config = self.BUTTON_STYLES.get(style, self.BUTTON_STYLES['default'])
        size_config = self.BUTTON_SIZES.get(size, self.BUTTON_SIZES['normal'])

        btn = tk.Button(parent,
                       text=text,
                       command=command,
                       bg=style_config['bg'],
                       fg=style_config['fg'],
                       activebackground=style_config['hover'],
                       activeforeground=style_config['fg'],
                       font=size_config['font'],
                       borderwidth=0,
                       highlightthickness=1,
                       highlightbackground=self.colors['border'],
                       highlightcolor=self.colors['accent'],
                       pady=size_config['pady'],
                       padx=size_config['padx'],
                       cursor='hand2',
                       relief='flat')
        btn.pack(side=side, padx=10)

        # Performance Optimization: Use shared class methods instead of redundant closure allocations
        btn._normal_bg = style_config['bg']
        btn._hover_bg = style_config['hover']
        btn._focus_bg = self.colors['accent']
        btn._focus_out_bg = self.colors['border']

        btn.bind("<Enter>", self._on_widget_enter)
        btn.bind("<Leave>", self._on_widget_leave)
        btn.bind("<FocusIn>", self._on_widget_focus_in)
        btn.bind("<FocusOut>", self._on_widget_focus_out)

        return btn

    def create_modern_checkbox(self, parent, text, variable):
        """Create a modern styled checkbox."""
        cb = tk.Checkbutton(parent,
                           text=text,
                           variable=variable,
                           bg=self.colors['surface'],
                           fg=self.colors['fg'],
                           selectcolor=self.colors['card'],
                           activebackground=self.colors['surface'],
                           activeforeground=self.colors['fg'],
                           font=('Segoe UI', self.base_font_size),
                           borderwidth=0,
                           highlightthickness=2,
                           highlightcolor=self.colors['accent'],
                           cursor='hand2')

        # Performance Optimization: Use shared class methods
        cb._focus_fg = self.colors['accent']
        cb._normal_fg = self.colors['fg']

        cb.bind("<FocusIn>", self._on_widget_focus_in)
        cb.bind("<FocusOut>", self._on_widget_focus_out)
        return cb

    # File and directory selection methods
    def select_files(self):
        """Select multiple Python files to convert with O(1) duplicate checks and batch insertion."""
        files = filedialog.askopenfilenames(
            filetypes=[("Python Files", "*.py"), ("All files", "*.*")],
            title="Select Python Files to Convert"
        )
        if files:
            # Optimization: Use a set for O(1) duplicate checks
            current_files = set(self.files_listbox.get(0, tk.END))
            new_files = [f for f in files if f not in current_files]

            if new_files:
                # Performance Optimization: Batch insertion into listbox reduces IPC overhead
                self.files_listbox.insert(tk.END, *new_files)
                for file in new_files:
                    self.log_output(f"Added file: {os.path.basename(file)}", "info")

    def remove_selected(self, listbox):
        """Remove selected items from a listbox."""
        selected = listbox.curselection()
        for index in selected[::-1]:
            item = listbox.get(index)
            listbox.delete(index)
            self.log_output(f"Removed: {os.path.basename(item) if os.path.exists(item) else item}", "info")

    def select_directory(self):
        """Select output directory for converted files."""
        directory = filedialog.askdirectory(
            title="Select Output Directory for EXE Files",
            initialdir=self.default_settings.get('default_output_dir', os.path.expanduser("~"))
        )
        if directory:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, directory)
            self.log_output(f"Output directory set: {directory}", "info")

    def select_icon_file(self):
        """Select an icon file for the executable."""
        icon_file = filedialog.askopenfilename(
            filetypes=[
                ("Icon Files", "*.ico"),
                ("Image Files", "*.png *.jpg *.jpeg *.bmp"),
                ("All files", "*.*")
            ],
            title="Select Icon File"
        )
        if icon_file:
            self.icon_entry.delete(0, tk.END)
            self.icon_entry.insert(0, icon_file)
            self.log_output(f"Icon file selected: {os.path.basename(icon_file)}", "info")

    def add_hidden_import(self):
        """Add a hidden import module."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Hidden Import")
        dialog.geometry("400x150")
        dialog.configure(bg=self.colors['surface'])
        dialog.resizable(False, False)

        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()

        # Module name entry
        tk.Label(dialog, text="Module name:", 
                bg=self.colors['surface'], fg=self.colors['fg'],
                font=('Segoe UI', self.base_font_size + 1)).pack(pady=10)
        
        entry_module = tk.Entry(dialog, width=40,
                               bg=self.colors['card'],
                               fg=self.colors['fg'],
                               insertbackground=self.colors['fg'],
                               highlightthickness=1,
                               highlightbackground=self.colors['border'],
                               highlightcolor=self.colors['accent'],
                               font=('Segoe UI', self.base_font_size + 1))
        entry_module.pack(pady=5)

        # Buttons
        button_frame = tk.Frame(dialog, bg=self.colors['surface'])
        button_frame.pack(pady=15)

        def add_to_list():
            module = entry_module.get().strip()
            if module:
                if module not in self.hidden_listbox.get(0, tk.END):
                    self.hidden_listbox.insert(tk.END, module)
                    self.log_output(f"Added hidden import: {module}", "success")
                    dialog.destroy()
                else:
                    messagebox.showinfo("Already Added", f"Module '{module}' is already in the list.")
            else:
                messagebox.showwarning("Invalid Input", "Please provide a module name.")

        self.create_modern_button(button_frame, "Add", add_to_list, 'left', style='success')
        self.create_modern_button(button_frame, "Cancel", dialog.destroy, 'left', style='danger')

        # Focus on entry and bind Enter key
        entry_module.focus_set()
        entry_module.bind('<Return>', lambda e: add_to_list())

    # Logging and validation methods
    def log_output(self, message, level="info"):
        """Log a message via a thread-safe queue. This is more efficient and prevents UI hangs."""
        if hasattr(self, 'log_queue'):
            self.log_queue.put((message, level))
        else:
            # Fallback for early logging if queue is not yet initialized
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] [{level.upper()}] {message}")

    def _setup_log_tags(self):
        """Configure color tags for the log output. Should be called after output_text creation or theme change."""
        if not hasattr(self, 'output_text'):
            return

        self.output_text.tag_config("timestamp", foreground=self.colors['border'])
        self.output_text.tag_config("info", foreground=self.colors['fg'])
        self.output_text.tag_config("success", foreground=self.colors['success'])
        self.output_text.tag_config("warning", foreground=self.colors['warning'])
        self.output_text.tag_config("error", foreground=self.colors['error'])

    def clear_log(self):
        """Clear the output log."""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.log_output("Log cleared", "info")

    def save_log(self):
        """Save the output log to a file."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Log File"
            )
            if filename:
                log_content = self.output_text.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                self.log_output(f"Log saved to: {filename}", "success")
        except Exception as e:
            self.log_output(f"Error saving log: {e}", "error")
            messagebox.showerror("Save Error", f"Could not save log file: {e}")

    def validate_settings(self):
        """Validate conversion settings before starting."""
        errors = []
        warnings = []

        # Check Python files
        files = list(self.files_listbox.get(0, tk.END))
        if not files:
            errors.append("No Python files selected for conversion")
        else:
            for file in files:
                if not os.path.exists(file):
                    errors.append(f"Python file not found: {file}")
                elif not file.endswith('.py'):
                    warnings.append(f"File may not be a Python script: {file}")

        # Check output directory
        output_dir = self.output_entry.get().strip()
        if not output_dir:
            errors.append("No output directory specified")
        elif not os.path.exists(output_dir):
            warnings.append(f"Output directory will be created: {output_dir}")

        # Check icon file
        icon_file = self.icon_entry.get().strip()
        if icon_file and not os.path.exists(icon_file):
            errors.append(f"Icon file not found: {icon_file}")
        elif not icon_file:
            # Show notification about using default icon
            if self.default_settings.get('show_icon_notifications', True):
                result = messagebox.askquestion("No Icon Specified",
                                              "⚠️ No icon file has been specified for the conversion.\n\n"
                                              "The default Python icon will be used for the executable.\n\n"
                                              "Do you want to continue with the conversion?",
                                              icon='question')
                if result == 'no':
                    errors.append("Conversion cancelled by user due to missing icon")
                else:
                    warnings.append("Using default Python icon (no custom icon specified)")
            else:
                warnings.append("Using default Python icon (no custom icon specified)")

        # Check PyInstaller availability (using cache if available)
        if not self._pyinstaller_version:
            try:
                result = subprocess.run(["pyinstaller", "--version"], capture_output=True, text=True, check=True)
                self._pyinstaller_version = result.stdout.strip()
            except (FileNotFoundError, subprocess.CalledProcessError):
                warnings.append("PyInstaller not found - will attempt to install")

        # Display results
        if errors:
            message = "Validation failed with errors:\n\n" + "\n".join(f"• {error}" for error in errors)
            if warnings:
                message += "\n\nWarnings:\n" + "\n".join(f"• {warning}" for warning in warnings)
            messagebox.showerror("Validation Failed", message)
            self.log_output("Validation failed", "error")
            for error in errors:
                self.log_output(f"Error: {error}", "error")
        else:
            message = "Validation successful! Ready to convert."
            if warnings:
                message += "\n\nWarnings:\n" + "\n".join(f"• {warning}" for warning in warnings)
                messagebox.showwarning("Validation Successful", message)
            else:
                messagebox.showinfo("Validation Successful", message)
            self.log_output("Settings validation passed", "success")

        return len(errors) == 0

    def _get_pyinstaller_status(self):
        """Get PyInstaller version with caching to improve performance."""
        if self._pyinstaller_version is not None:
            return self._pyinstaller_version

        try:
            result = subprocess.run(["pyinstaller", "--version"],
                                  capture_output=True, text=True, check=True)
            self._pyinstaller_version = result.stdout.strip()
            return self._pyinstaller_version
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

    def install_pyinstaller(self):
        """Install PyInstaller if not available."""
        try:
            self.log_output("Installing PyInstaller...", "info")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

            # Reset cache and verify installation
            self._pyinstaller_version = None
            if self._get_pyinstaller_status():
                self.log_output("PyInstaller installed successfully", "success")
                return True
            else:
                raise Exception("Installation appeared successful but PyInstaller is still not found")

        except Exception as e:
            self.log_output(f"Failed to install PyInstaller: {e}", "error")
            messagebox.showerror("Installation Error", f"Failed to install PyInstaller: {e}")
            return False

    def convert_to_exe(self):
        """Main conversion function with enhanced error handling."""
        if not self.validate_settings():
            return

        files = list(self.files_listbox.get(0, tk.END))
        output_dir = self.output_entry.get().strip()

        # Check and install PyInstaller if necessary (using cache if available)
        if not self._pyinstaller_version:
            try:
                result = subprocess.run(["pyinstaller", "--version"], capture_output=True, text=True, check=True)
                self._pyinstaller_version = result.stdout.strip()
            except (FileNotFoundError, subprocess.CalledProcessError):
                if not self.install_pyinstaller():
                    return

        # Disable convert button and start progress
        self.convert_btn.config(state=tk.DISABLED, text="🔄 Converting...")
        self.progress_var.set(0)
        self.progress_bar.config(mode='determinate', maximum=len(files))

        def run_conversion():
            """Run the conversion process in a separate thread."""
            successful_conversions = 0

            try:
                # Create output directory if it doesn't exist
                os.makedirs(output_dir, exist_ok=True)

                # Performance Optimization: Extract loop-invariant configurations before processing loop
                # This minimizes redundant Tcl interpreter calls and filesystem checks during batch conversions
                use_onefile = self.onefile_var.get()
                use_noconsole = self.noconsole_var.get()
                use_debug = self.debug_var.get()
                icon_file = self.icon_entry.get().strip()
                icon_valid = icon_file and os.path.exists(icon_file)
                hidden_imports_list = list(self.hidden_listbox.get(0, tk.END))

                # Optimization: Single UI update before loop instead of every iteration
                self.root.after(0, lambda: self.convert_btn.config(text="⏳ Converting..."))

                for i, file in enumerate(files):
                    try:
                        self.log_output(f"Converting {os.path.basename(file)}...", "info")

                        # Build PyInstaller command
                        cmd = ["pyinstaller"]

                        # Add options
                        if use_onefile:
                            cmd.append("--onefile")
                        if use_noconsole:
                            cmd.append("--noconsole")
                        if use_debug:
                            cmd.append("--debug")

                        # Add icon
                        if icon_valid:
                            cmd.extend(["--icon", icon_file])

                        # Add hidden imports
                        for hidden in hidden_imports_list:
                            cmd.extend(["--hidden-import", hidden])

                        # Set output directory
                        cmd.extend(["--distpath", output_dir])

                        # Clean previous builds
                        cmd.append("--clean")

                        # Add the Python file
                        cmd.append(file)

                        # Run PyInstaller
                        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

                        self.log_output(f"✅ Successfully converted {os.path.basename(file)}", "success")
                        successful_conversions += 1

                        # Optimization: Use root.after for thread-safe UI updates
                        self.root.after(0, lambda v=i+1: self.progress_var.set(v))

                    except subprocess.CalledProcessError as e:
                        error_msg = f"❌ Error converting {os.path.basename(file)}: {e}"
                        self.log_output(error_msg, "error")
                        if e.stderr:
                            self.log_output(f"Error details: {e.stderr[:500]}...", "error")
                    except Exception as e:
                        error_msg = f"❌ Unexpected error converting {os.path.basename(file)}: {e}"
                        self.log_output(error_msg, "error")

                # Final summary
                if successful_conversions > 0:
                    self.log_output(f"🎉 Conversion completed! {successful_conversions}/{len(files)} files converted successfully.", "success")
                    msg = f"Successfully converted {successful_conversions} out of {len(files)} files.\n\nOutput directory: {output_dir}"
                    self.root.after(0, lambda m=msg: messagebox.showinfo("Conversion Complete", m))
                else:
                    self.log_output("❌ Conversion failed for all files.", "error")
                    self.root.after(0, lambda: messagebox.showerror("Conversion Failed", "No files were successfully converted."))

            except Exception as e:
                error_msg = f"❌ Critical error during conversion: {e}"
                self.log_output(error_msg, "error")
                self.root.after(0, lambda m=error_msg: messagebox.showerror("Critical Error", m))

            finally:
                # Optimization: Ensure all final UI updates are scheduled on the main thread
                self.root.after(0, lambda: self.convert_btn.config(state=tk.NORMAL, text="🔄 Convert to EXE"))
                self.root.after(0, lambda: self.progress_var.set(0))
                if hasattr(self, 'status_label'):
                    self.root.after(0, lambda: self.status_label.config(text="Conversion completed"))

        # Run conversion in a separate thread
        threading.Thread(target=run_conversion, daemon=True).start()

    # Placeholder methods for tabs (simplified version)
    def create_icon_manager_tab(self):
        """Create the comprehensive icon manager tab with shape options."""
        self.icon_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.icon_frame, text="🎨 Icon Manager")

        # Create main container with scrollable canvas
        canvas = tk.Canvas(self.icon_frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.icon_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Icon creator section
        creator_frame = ttk.LabelFrame(scrollable_frame, text="🖼️ Icon Creator")
        creator_frame.pack(fill='x', padx=15, pady=10)

        # Source image selection
        source_frame = tk.Frame(creator_frame, bg=self.colors['surface'])
        source_frame.pack(fill='x', padx=15, pady=15)

        ttk.Label(source_frame, text="Source Image:").pack(side='left')

        self.source_image_entry = tk.Entry(source_frame,
                                          bg=self.colors['card'],
                                          fg=self.colors['fg'],
                                          insertbackground=self.colors['fg'],
                                          borderwidth=0,
                                          highlightthickness=1,
                                          highlightbackground=self.colors['border'],
                                          highlightcolor=self.colors['accent'],
                                          font=('Segoe UI', self.base_font_size + 1))
        self.source_image_entry.pack(side='left', fill='x', expand=True, padx=15)
        self._add_placeholder(self.source_image_entry, "Path to source image (PNG, JPG)...")

        btn_browse_src = self.create_modern_button(source_frame, "📁 Browse",
                                 lambda: self.select_source_image(), 'right', style='primary')
        self.create_tooltip(btn_browse_src, "Select an image to create a custom icon from")

        # Icon shape selection
        shape_frame = tk.Frame(creator_frame, bg=self.colors['surface'])
        shape_frame.pack(fill='x', padx=15, pady=10)

        ttk.Label(shape_frame, text="Icon Shape:").pack(side='left')

        self.shape_var = tk.StringVar(value='Square with Rounded Corners')
        shape_dropdown = ttk.Combobox(shape_frame, textvariable=self.shape_var,
                                     values=list(self.icon_shapes.values()),
                                     state='readonly', width=25)
        shape_dropdown.pack(side='left', padx=15)

        # Preview frame
        preview_frame = tk.Frame(creator_frame, bg=self.colors['surface'])
        preview_frame.pack(fill='x', padx=15, pady=10)

        ttk.Label(preview_frame, text="Preview:").pack(side='left')

        self.preview_frame = tk.Frame(preview_frame, bg=self.colors['card'],
                                     width=100, height=100, relief='flat', borderwidth=0,
                                     highlightthickness=1, highlightbackground=self.colors['border'])
        self.preview_frame.pack(side='left', padx=15)
        self.preview_frame.pack_propagate(False)

        # Bind events for real-time preview
        self.source_image_entry.bind('<KeyRelease>', lambda e: self.update_icon_preview())
        shape_dropdown.bind('<<ComboboxSelected>>', lambda e: self.update_icon_preview())

        # Icon size options
        size_frame = tk.Frame(creator_frame, bg=self.colors['surface'])
        size_frame.pack(fill='x', padx=15, pady=10)

        ttk.Label(size_frame, text="Icon Sizes:").pack(side='left')

        # Create a frame for checkboxes using pack manager
        checkbox_frame = tk.Frame(size_frame, bg=self.colors['surface'])
        checkbox_frame.pack(side='left', padx=15)

        self.size_vars = {}
        sizes = ['16x16', '32x32', '48x48', '64x64', '128x128', '256x256']
        row1_frame = tk.Frame(checkbox_frame, bg=self.colors['surface'])
        row1_frame.pack(fill='x')
        row2_frame = tk.Frame(checkbox_frame, bg=self.colors['surface'])
        row2_frame.pack(fill='x')

        for i, size in enumerate(sizes):
            var = tk.BooleanVar(value=True if size in ['32x32', '48x48', '256x256'] else False)
            self.size_vars[size] = var
            parent_frame = row1_frame if i < 3 else row2_frame
            cb = self.create_modern_checkbox(parent_frame, size, var)
            cb.pack(side='left', padx=10)

        # Create icon button
        create_frame = tk.Frame(creator_frame, bg=self.colors['surface'])
        create_frame.pack(fill='x', padx=15, pady=15)

        self.create_icon_btn = self.create_modern_button(create_frame, "🎨 Create Shaped Icon",
                                                        self.create_icon_from_image, 'left',
                                                        style='success', size='large')
        self.create_tooltip(self.create_icon_btn, "Generate icon files in the selected shape and sizes")

        # Icon browser section
        browser_frame = ttk.LabelFrame(scrollable_frame, text="🔍 Icon Browser")
        browser_frame.pack(fill='both', expand=True, padx=15, pady=10)

        # Search controls
        search_frame = tk.Frame(browser_frame, bg=self.colors['surface'])
        search_frame.pack(fill='x', padx=15, pady=15)

        ttk.Label(search_frame, text="Search Directory:").pack(side='left')

        self.search_entry = tk.Entry(search_frame,
                                    bg=self.colors['card'],
                                    fg=self.colors['fg'],
                                    insertbackground=self.colors['fg'],
                                    borderwidth=0,
                                    highlightthickness=1,
                                    highlightbackground=self.colors['border'],
                                    highlightcolor=self.colors['accent'],
                                    font=('Segoe UI', self.base_font_size + 1))
        self.search_entry.pack(side='left', fill='x', expand=True, padx=15)
        self._add_placeholder(self.search_entry, "Directory to search for icons...")

        btn_browse_search = self.create_modern_button(search_frame, "📁 Browse",
                                 self.select_search_directory, 'right')
        self.create_tooltip(btn_browse_search, "Choose a folder to search for existing icons")

        btn_search = self.create_modern_button(search_frame, "🔍 Search",
                                 self.search_icons, 'right', style='primary')
        self.create_tooltip(btn_search, "Find icon files in the selected directory")

        # Icons display area
        self.create_icons_display(browser_frame)

    def create_icons_display(self, parent):
        """Create the icons display area with previews."""
        display_frame = tk.Frame(parent, bg=self.colors['surface'])
        display_frame.pack(fill='both', expand=True, padx=15, pady=15)

        # Empty state label
        self.empty_icons_label = tk.Label(display_frame,
                                         text="🔍 Search for icons to see them here!",
                                         bg=self.colors['surface'],
                                         fg=self.colors['border'],
                                         font=('Segoe UI', self.base_font_size + 2))
        self.empty_icons_label.place(relx=0.5, rely=0.5, anchor='center')

        # Create canvas for icon grid
        self.icons_canvas = tk.Canvas(display_frame, 
                                     bg=self.colors['card'],
                                     highlightthickness=0)
        icons_scrollbar = ttk.Scrollbar(display_frame, orient="vertical", 
                                       command=self.icons_canvas.yview)
        self.icons_scrollable_frame = tk.Frame(self.icons_canvas, bg=self.colors['card'])

        self.icons_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.icons_canvas.configure(scrollregion=self.icons_canvas.bbox("all"))
        )

        self.icons_canvas.create_window((0, 0), window=self.icons_scrollable_frame, anchor="nw")
        self.icons_canvas.configure(yscrollcommand=icons_scrollbar.set)

        self.icons_canvas.pack(side="left", fill="both", expand=True)
        icons_scrollbar.pack(side="right", fill="y")

        # Icon selection info
        info_frame = tk.Frame(parent, bg=self.colors['surface'])
        info_frame.pack(fill='x', padx=15, pady=10)

        self.selected_icon_label = tk.Label(info_frame,
                                           text="No icon selected",
                                           bg=self.colors['surface'],
                                           fg=self.colors['fg'],
                                           font=('Segoe UI', self.base_font_size + 1))
        self.selected_icon_label.pack(side='left')

        self.create_modern_button(info_frame, "✅ Use Selected Icon",
                                 self.use_selected_icon, 'right', style='success')

    # Icon creation and management methods
    def select_source_image(self):
        """Select source image for icon creation."""
        image_file = filedialog.askopenfilename(
            title="Select Source Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        if image_file:
            self.source_image_entry.delete(0, tk.END)
            self.source_image_entry.insert(0, image_file)
            self.update_icon_preview()

    def update_icon_preview(self):
        """Update the icon preview when source image changes with efficiency checks and fast resampling."""
        source_path = self.source_image_entry.get().strip()

        # Performance Optimization: Only proceed if the path is actually a file.
        # This avoids unnecessary attempts to open directories or partial paths.
        if source_path and os.path.isfile(source_path):
            try:
                # Clear existing preview
                for widget in self.preview_frame.winfo_children():
                    widget.destroy()

                # Create preview
                with Image.open(source_path) as img:
                    # Performance Optimization: Use BOX resampling for fast thumbnail generation.
                    # BOX is significantly faster than LANCZOS for small previews.
                    preview_img = img.resize((80, 80), Image.Resampling.BOX)
                    preview_photo = ImageTk.PhotoImage(preview_img)

                    preview_label = tk.Label(self.preview_frame, image=preview_photo,
                                           bg=self.colors['card'])
                    preview_label.pack(expand=True)

                    # Keep reference to prevent garbage collection
                    preview_label.image = preview_photo

            except Exception as e:
                # Show error in preview
                error_label = tk.Label(self.preview_frame, text="Invalid\nImage",
                                      bg=self.colors['card'], fg=self.colors['error'],
                                      font=('Segoe UI', self.base_font_size))
                error_label.pack(expand=True)

    def create_icon_from_image(self):
        """Create shaped icon files from source image."""
        source_image = self.source_image_entry.get().strip()
        if not source_image or not os.path.exists(source_image):
            messagebox.showerror("Error", "Please select a valid source image.")
            return

        # Get selected sizes and shape
        selected_sizes = [size for size, var in self.size_vars.items() if var.get()]
        if not selected_sizes:
            messagebox.showerror("Error", "Please select at least one icon size.")
            return

        # Get selected shape
        shape_display = self.shape_var.get()
        shape_key = None
        for key, display in self.icon_shapes.items():
            if display == shape_display:
                shape_key = key
                break

        if not shape_key:
            shape_key = 'square'

        # Ask for output directory - use default if available
        default_dir = self.default_settings.get('default_icon_output_dir',
                                               os.path.join(os.path.expanduser("~"), "Desktop"))
        output_dir = filedialog.askdirectory(title="Select Output Directory for Shaped Icons",
                                            initialdir=default_dir)
        if not output_dir:
            return

        try:
            if hasattr(self, 'log_output'):
                self.log_output(f"Creating {shape_display.lower()} icons from {os.path.basename(source_image)}...", "info")

            # Open source image
            with Image.open(source_image) as img:
                # Convert to RGBA if necessary
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')

                base_name = os.path.splitext(os.path.basename(source_image))[0]
                created_icons = []

                # Optimization: Resize source image to max required size once
                # This avoids expensive resizing of large source images for every target size
                sizes = [int(s.split('x')[0]) for s in selected_sizes]
                max_size = max(sizes)

                working_img = img
                if img.width > max_size and img.height > max_size:
                    if hasattr(self, 'log_output'):
                        self.log_output(f"Optimizing: Pre-resizing source image to {max_size}x{max_size}...", "info")
                    working_img = img.resize((max_size, max_size), Image.Resampling.LANCZOS)

                # Performance Optimization: Sort sizes in descending order for progressive resizing
                # This significantly reduces computational load by resizing from the next largest image.
                # Quality Optimization: We maintain an unmasked source for resizing to prevent quality loss
                # and redundant alpha-channel processing during progressive downscaling.
                sorted_sizes = sorted(sizes, reverse=True)
                size_to_shaped_img = {}
                current_unmasked = working_img

                for size in sorted_sizes:
                    # 1. Resize the unmasked image to target size
                    if current_unmasked.size == (size, size):
                        resized_unmasked = current_unmasked
                    else:
                        resized_unmasked = current_unmasked.resize((size, size), Image.Resampling.LANCZOS)

                    # 2. Apply shape/mask to the correctly-sized unmasked image (create_shaped_icon handles the masking)
                    shaped_icon = self.create_shaped_icon(resized_unmasked, shape_key, size)
                    size_to_shaped_img[size] = shaped_icon

                    # 3. Use this unmasked resized image as source for the next smaller size
                    current_unmasked = resized_unmasked

                    # Save as ICO
                    ico_path = os.path.join(output_dir, f"{base_name}_{shape_key}_{size}x{size}.ico")
                    shaped_icon.save(ico_path, format='ICO')
                    created_icons.append(ico_path)

                    if hasattr(self, 'log_output'):
                        self.log_output(f"Created {size}x{size} {shape_display.lower()} icon: {os.path.basename(ico_path)}", "success")

                # Create multi-size ICO with shape
                multi_ico_path = os.path.join(output_dir, f"{base_name}_{shape_key}_multi.ico")

                # Use pre-calculated icons for multi-size ICO
                shaped_icons = [size_to_shaped_img[s] for s in sizes]

                if shaped_icons:
                    shaped_icons[0].save(multi_ico_path, format='ICO',
                                       append_images=shaped_icons[1:] if len(shaped_icons) > 1 else [],
                                       sizes=[(s, s) for s in sizes])
                    created_icons.append(multi_ico_path)

                    if hasattr(self, 'log_output'):
                        self.log_output(f"Created multi-size {shape_display.lower()} icon: {os.path.basename(multi_ico_path)}", "success")

                # Auto-select the multi-size icon for conversion if enabled
                if self.default_settings.get('auto_select_created_icons', True) and created_icons:
                    # Use the multi-size icon if available, otherwise use the first created icon
                    icon_to_select = multi_ico_path if multi_ico_path in created_icons else created_icons[0]
                    if hasattr(self, 'icon_entry'):
                        self.icon_entry.delete(0, tk.END)
                        self.icon_entry.insert(0, icon_to_select)
                    self.last_created_icon = icon_to_select
                    if hasattr(self, 'log_output'):
                        self.log_output(f"Auto-selected icon: {os.path.basename(icon_to_select)}", "info")

                # Show notification if enabled
                if self.default_settings.get('show_icon_notifications', True):
                    messagebox.showinfo("Shaped Icons Created",
                                       f"Successfully created {len(created_icons)} {shape_display.lower()} icon files!\n\n" +
                                       (f"✅ Auto-selected for conversion: {os.path.basename(icon_to_select)}\n\n" if self.default_settings.get('auto_select_created_icons', True) and created_icons else "") +
                                       "\n".join(os.path.basename(icon) for icon in created_icons) +
                                       f"\n\n📁 Output directory: {output_dir}")
                else:
                    # Just show a simple success message
                    if hasattr(self, 'log_output'):
                        self.log_output(f"Created {len(created_icons)} icon files in {output_dir}", "success")

                # Refresh icon browser if searching in the same directory
                if self.search_entry.get().strip() == output_dir:
                    self.search_icons()

        except Exception as e:
            error_msg = f"Error creating shaped icons: {e}"
            if hasattr(self, 'log_output'):
                self.log_output(error_msg, "error")
            messagebox.showerror("Icon Creation Error", error_msg)

    def _get_shape_mask(self, shape, size, **kwargs):
        """Create and cache a shape mask to improve performance."""
        # Create a stable cache key based on shape, size and additional arguments
        mask_key = (shape, size, tuple(sorted(kwargs.items())))
        if mask_key in self._mask_cache:
            self._mask_cache.move_to_end(mask_key)
            return self._mask_cache[mask_key]

        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)

        if shape == 'circle':
            draw.ellipse([0, 0, size - 1, size - 1], fill=255)
        elif shape == 'triangle':
            points = [(size // 2, 5), (5, size - 5), (size - 5, size - 5)]
            draw.polygon(points, fill=255)
        elif shape == 'hexagon':
            center = size // 2
            radius = center - 5
            # Performance Optimization: Use pre-calculated vertices to avoid trigonometric calculations
            points = [(center + radius * x, center + radius * y) for x, y in self.HEX_VERTICES]
            draw.polygon(points, fill=255)
        elif shape == 'star':
            center = size // 2
            radius = center - 5
            # Performance Optimization: Use pre-calculated vertices to avoid trigonometric calculations
            points = [(center + radius * x, center + radius * y) for x, y in self.STAR_VERTICES]
            draw.polygon(points, fill=255)
        elif shape == 'diamond':
            center = size // 2
            points = [(center, 5), (size - 5, center), (center, size - 5), (5, center)]
            draw.polygon(points, fill=255)
        else:  # 'square' or default
            radius = kwargs.get('radius', size // 8)
            draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)

        self._mask_cache[mask_key] = mask
        if len(self._mask_cache) > self.MAX_MASK_CACHE:
            self._mask_cache.popitem(last=False)

        return mask

    def create_shaped_icon(self, image, shape, size):
        """Create an icon with the specified shape using caching and optimized alpha application."""
        # Performance Optimization: Use image identity in cache key with identity verification
        cache_key = (id(image), shape, size)
        if cache_key in self.shaped_icons_cache:
            img, ref = self.shaped_icons_cache[cache_key]
            if ref() is image:
                self.shaped_icons_cache.move_to_end(cache_key)
                return img
            # If identity verification fails (ID reuse), remove the stale entry
            del self.shaped_icons_cache[cache_key]

        # Performance Optimization: Skip resize if already at target size
        if image.size == (size, size):
            # Performance Optimization: convert('RGBA') always returns a copy,
            # so we avoid separate copy() + convert() calls for non-RGBA sources
            img = image.convert('RGBA')
        else:
            img = image.resize((size, size), Image.Resampling.LANCZOS)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

        # Get mask from cache or create it
        kwargs = {}
        if shape not in ['circle', 'triangle', 'hexagon', 'star', 'diamond']:
            kwargs['radius'] = size // 8

        mask = self._get_shape_mask(shape, size, **kwargs)

        # Performance Optimization: Apply mask directly to resized image using putalpha
        img.putalpha(mask)

        # Store in LRU cache with identity verification to prevent memory leaks and ID reuse bugs
        self.shaped_icons_cache[cache_key] = (img, weakref.ref(image))
        if len(self.shaped_icons_cache) > self.MAX_SHAPED_ICONS:
            self.shaped_icons_cache.popitem(last=False)

        return img

    def select_search_directory(self):
        """Select directory to search for icons."""
        directory = filedialog.askdirectory(
            title="Select Directory to Search for Icons",
            initialdir=self.search_entry.get() or self.default_settings.get('default_icon_output_dir',
                                                                           os.path.join(os.path.expanduser("~"), "Desktop"))
        )
        if directory:
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, directory)

    def _iter_icons(self, directory, extensions, limit):
        """Internal recursive generator for efficient icon discovery using os.scandir."""
        # Performance Optimization: Yield string paths directly instead of Path objects to minimize overhead
        count = 0
        try:
            with os.scandir(directory) as it:
                for entry in it:
                    if count >= limit:
                        return
                    if entry.is_file() and entry.name.lower().endswith(extensions):
                        yield entry.path
                        count += 1
                    elif entry.is_dir():
                        # Performance Optimization: Skip hidden and common large or irrelevant directories
                        # to significantly reduce filesystem I/O and traversal time.
                        name = entry.name.lower()
                        if name.startswith('.') or name in ('node_modules', 'venv', '.venv', '__pycache__', 'build', 'dist', 'target'):
                            continue

                        # Recursively search subdirectories
                        for icon in self._iter_icons(entry.path, extensions, limit - count):
                            yield icon
                            count += 1
                            if count >= limit:
                                return
        except (PermissionError, OSError):
            pass

    def search_icons(self):
        """Search for icon files in the specified directory using an efficient recursive generator."""
        search_dir = self.search_entry.get().strip()
        # Handle placeholder
        if search_dir == "Directory to search for icons...":
            search_dir = ""

        if not search_dir or not os.path.exists(search_dir):
            messagebox.showerror("Error", "Please select a valid directory to search.")
            return

        # Clear previous results
        for widget in self.icons_scrollable_frame.winfo_children():
            widget.destroy()

        # Hide empty state label
        self.empty_icons_label.place_forget()

        # Performance Optimization: Use os.scandir with a recursive generator for faster traversal and immediate termination
        extensions = ('.ico', '.png', '.jpg', '.jpeg', '.bmp')
        # Performance Optimization: Match search limit to display limit (20) to minimize wasted I/O
        limit = 20

        icon_files = list(self._iter_icons(search_dir, extensions, limit))
        found_count = len(icon_files)

        if found_count == 0:
            self.empty_icons_label.config(text="❌ No icons found in this directory.")
            self.empty_icons_label.place(relx=0.5, rely=0.5, anchor='center')
            return

        # Display found icons
        if hasattr(self, 'log_output'):
            msg = f"Found {found_count} icon files"
            if found_count >= limit:
                msg += f" (stopped searching at {limit} for performance)"
            self.log_output(msg, "info")

        # Create grid of icon previews
        columns = 4
        # Display a subset of found icons to maintain UI performance
        display_limit = 20
        for i, icon_path in enumerate(icon_files[:display_limit]):
            row = i // columns
            col = i % columns

            icon_frame = tk.Frame(self.icons_scrollable_frame, bg=self.colors['card'])
            icon_frame.grid(row=row, column=col, padx=10, pady=10, sticky='w')

            try:
                # Create icon preview
                with Image.open(icon_path) as img:
                    # Performance Optimization: Use BOX resampling for fast thumbnail generation.
                    img.thumbnail((64, 64), Image.Resampling.BOX)
                    icon_photo = ImageTk.PhotoImage(img)

                    icon_btn = tk.Button(icon_frame,
                                        image=icon_photo,
                                        command=lambda p=str(icon_path): self.select_icon_preview(p),
                                        bg=self.colors['card'],
                                        activebackground=self.colors['surface'],
                                        relief='flat',
                                        borderwidth=0,
                                        highlightthickness=1,
                                        highlightbackground=self.colors['border'],
                                        cursor='hand2')
                    icon_btn.pack()

                    # Keep reference to prevent garbage collection
                    icon_btn.image = icon_photo

                    # Icon filename label
                    name_label = tk.Label(icon_frame,
                                         text=icon_path.name[:15] + "..." if len(icon_path.name) > 15 else icon_path.name,
                                         bg=self.colors['card'],
                                         fg=self.colors['fg'],
                                         font=('Segoe UI', self.base_font_size - 1))
                    name_label.pack()

            except Exception as e:
                # Fallback for unreadable images
                error_label = tk.Label(icon_frame,
                                      text="Invalid\nImage",
                                      bg=self.colors['card'],
                                      fg=self.colors['error'],
                                      font=('Segoe UI', self.base_font_size - 1))
                error_label.pack()

    def select_icon_preview(self, icon_path):
        """Select an icon from the preview grid."""
        self.selected_icon.set(icon_path)
        self.selected_icon_label.config(text=f"Selected: {os.path.basename(icon_path)}")
        if hasattr(self, 'log_output'):
            self.log_output(f"Selected icon: {os.path.basename(icon_path)}", "info")

    def use_selected_icon(self):
        """Use the selected icon for conversion."""
        icon_path = self.selected_icon.get()
        if icon_path:
            if hasattr(self, 'icon_entry'):
                self.icon_entry.delete(0, tk.END)
                self.icon_entry.insert(0, icon_path)
            if hasattr(self, 'log_output'):
                self.log_output(f"Using icon: {os.path.basename(icon_path)}", "success")
            messagebox.showinfo("Icon Selected", f"Icon selected for conversion:\n{os.path.basename(icon_path)}")
        else:
            messagebox.showwarning("No Selection", "Please select an icon first.")

    def create_settings_tab(self):
        """Create the comprehensive settings tab for customizing application behavior."""
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="⚙️ Settings")

        # Create main container with scrollable canvas
        canvas = tk.Canvas(self.settings_frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.settings_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Default Directories Section
        self.create_directories_settings(scrollable_frame)

        # Appearance Settings Section
        self.create_appearance_settings(scrollable_frame)

        # Behavior Settings Section
        self.create_behavior_settings(scrollable_frame)

        # Settings Controls
        self.create_settings_controls(scrollable_frame)

    def create_directories_settings(self, parent):
        """Create default directories settings section."""
        dirs_frame = ttk.LabelFrame(parent, text="📁 Default Directories")
        dirs_frame.pack(fill='x', padx=15, pady=10)

        # Default EXE Output Directory
        exe_dir_frame = tk.Frame(dirs_frame, bg=self.colors['surface'])
        exe_dir_frame.pack(fill='x', padx=15, pady=10)

        ttk.Label(exe_dir_frame, text="Default EXE Output Directory:").pack(anchor='w')

        exe_entry_frame = tk.Frame(exe_dir_frame, bg=self.colors['surface'])
        exe_entry_frame.pack(fill='x', pady=5)

        self.default_exe_dir_var = tk.StringVar(value=self.default_settings['default_output_dir'])
        self.default_exe_dir_entry = tk.Entry(exe_entry_frame,
                                             textvariable=self.default_exe_dir_var,
                                             bg=self.colors['card'],
                                             fg=self.colors['fg'],
                                             insertbackground=self.colors['fg'],
                                             borderwidth=0,
                                             highlightthickness=1,
                                             highlightbackground=self.colors['border'],
                                             highlightcolor=self.colors['accent'],
                                             font=('Segoe UI', self.base_font_size + 1))
        self.default_exe_dir_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))

        self.create_modern_button(exe_entry_frame, "📁 Browse",
                                 lambda: self.browse_default_exe_dir(), 'right')

        # Default Icon Output Directory
        icon_dir_frame = tk.Frame(dirs_frame, bg=self.colors['surface'])
        icon_dir_frame.pack(fill='x', padx=15, pady=10)

        ttk.Label(icon_dir_frame, text="Default Icon Output Directory:").pack(anchor='w')

        icon_entry_frame = tk.Frame(icon_dir_frame, bg=self.colors['surface'])
        icon_entry_frame.pack(fill='x', pady=5)

        self.default_icon_dir_var = tk.StringVar(value=self.default_settings['default_icon_output_dir'])
        self.default_icon_dir_entry = tk.Entry(icon_entry_frame,
                                              textvariable=self.default_icon_dir_var,
                                              bg=self.colors['card'],
                                              fg=self.colors['fg'],
                                              insertbackground=self.colors['fg'],
                                              borderwidth=0,
                                              highlightthickness=1,
                                              highlightbackground=self.colors['border'],
                                              highlightcolor=self.colors['accent'],
                                              font=('Segoe UI', self.base_font_size + 1))
        self.default_icon_dir_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))

        self.create_modern_button(icon_entry_frame, "📁 Browse",
                                 lambda: self.browse_default_icon_dir(), 'right')

    def create_appearance_settings(self, parent):
        """Create appearance settings section."""
        appearance_frame = ttk.LabelFrame(parent, text="🎨 Appearance")
        appearance_frame.pack(fill='x', padx=15, pady=10)

        # Window Transparency
        transparency_frame = tk.Frame(appearance_frame, bg=self.colors['surface'])
        transparency_frame.pack(fill='x', padx=15, pady=10)

        ttk.Label(transparency_frame, text="Window Transparency:").pack(side='left')

        self.transparency_var = tk.DoubleVar(value=self.default_settings['window_transparency'])
        transparency_scale = tk.Scale(transparency_frame,
                                     from_=0.7, to=1.0, resolution=0.05,
                                     variable=self.transparency_var,
                                     orient=tk.HORIZONTAL,
                                     bg=self.colors['surface'],
                                     fg=self.colors['fg'],
                                     activebackground=self.colors['accent'],
                                     troughcolor=self.colors['card'],
                                     highlightthickness=0,
                                     command=self.update_transparency)
        transparency_scale.pack(side='left', fill='x', expand=True, padx=10)

        # Transparency value display
        self.transparency_label = tk.Label(transparency_frame, 
                                          text=f"{self.transparency_var.get():.0%}",
                                          bg=self.colors['surface'], fg=self.colors['fg'],
                                          font=('Segoe UI', self.base_font_size))
        self.transparency_label.pack(side='right', padx=10)

        # Theme Selection (if available)
        if hasattr(self, 'available_themes'):
            theme_frame = tk.Frame(appearance_frame, bg=self.colors['surface'])
            theme_frame.pack(fill='x', padx=15, pady=10)

            ttk.Label(theme_frame, text="Theme:").pack(side='left')

            self.theme_var = tk.StringVar(value=self.default_settings.get('theme', 'dark'))
            theme_dropdown = ttk.Combobox(theme_frame, textvariable=self.theme_var,
                                         values=list(self.available_themes.keys()) if hasattr(self, 'available_themes') else ['dark', 'light'],
                                         state='readonly', width=15)
            theme_dropdown.pack(side='left', padx=15)
            theme_dropdown.bind('<<ComboboxSelected>>', self.on_theme_changed)

    def create_behavior_settings(self, parent):
        """Create behavior settings section."""
        behavior_frame = ttk.LabelFrame(parent, text="🔧 Behavior")
        behavior_frame.pack(fill='x', padx=15, pady=10)

        behavior_container = tk.Frame(behavior_frame, bg=self.colors['surface'])
        behavior_container.pack(fill='x', padx=15, pady=15)

        # Auto-select created icons
        self.auto_select_icons_var = tk.BooleanVar(value=self.default_settings['auto_select_created_icons'])
        auto_select_cb = self.create_modern_checkbox(behavior_container,
                                                    "🎯 Automatically select newly created icons for conversion",
                                                    self.auto_select_icons_var)
        auto_select_cb.pack(anchor='w', pady=5)

        # Show icon notifications
        self.show_notifications_var = tk.BooleanVar(value=self.default_settings['show_icon_notifications'])
        notifications_cb = self.create_modern_checkbox(behavior_container,
                                                      "🔔 Show notifications when icons are created",
                                                      self.show_notifications_var)
        notifications_cb.pack(anchor='w', pady=5)

        # Auto-search icons on startup
        self.auto_search_icons_var = tk.BooleanVar(value=self.default_settings.get('auto_search_icons', False))
        auto_search_cb = self.create_modern_checkbox(behavior_container,
                                                    "🔍 Automatically search for icons in default directory on startup",
                                                    self.auto_search_icons_var)
        auto_search_cb.pack(anchor='w', pady=5)

        # Validate before conversion
        self.validate_before_convert_var = tk.BooleanVar(value=self.default_settings.get('validate_before_convert', True))
        validate_cb = self.create_modern_checkbox(behavior_container,
                                                 "✅ Always validate settings before conversion",
                                                 self.validate_before_convert_var)
        validate_cb.pack(anchor='w', pady=5)

    def create_settings_controls(self, parent):
        """Create settings control buttons."""
        controls_frame = ttk.LabelFrame(parent, text="💾 Settings Controls")
        controls_frame.pack(fill='x', padx=15, pady=10)

        button_frame = tk.Frame(controls_frame, bg=self.colors['surface'])
        button_frame.pack(fill='x', padx=15, pady=15)

        self.create_modern_button(button_frame, "💾 Save Settings",
                                 self.save_current_settings, 'left', style='success')
        self.create_modern_button(button_frame, "🔄 Reset to Defaults",
                                 self.reset_to_defaults, 'left', style='warning')
        self.create_modern_button(button_frame, "✅ Apply Changes",
                                 self.apply_settings_changes, 'left', style='primary')

        # Settings status
        status_frame = tk.Frame(controls_frame, bg=self.colors['surface'])
        status_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        self.settings_status_label = tk.Label(status_frame,
                                             text="💡 Settings are automatically applied when changed",
                                             bg=self.colors['surface'],
                                             fg=self.colors['fg'],
                                             font=('Segoe UI', self.base_font_size),
                                             anchor='w')
        self.settings_status_label.pack(fill='x')

        # Current settings summary
        summary_frame = ttk.LabelFrame(parent, text="📋 Current Settings Summary")
        summary_frame.pack(fill='x', padx=15, pady=10)

        self.create_settings_summary(summary_frame)

    def create_settings_summary(self, parent):
        """Create a summary of current settings."""
        summary_container = tk.Frame(parent, bg=self.colors['surface'])
        summary_container.pack(fill='x', padx=15, pady=15)
        
        # Create summary text
        summary_text = tk.Text(summary_container,
                              height=8,
                              bg=self.colors['card'],
                              fg=self.colors['fg'],
                              font=self.mono_font,
                              wrap=tk.WORD,
                              borderwidth=0,
                              highlightthickness=1,
                              highlightbackground=self.colors['border'],
                              highlightcolor=self.colors['accent'],
                              state=tk.DISABLED)
        summary_text.pack(fill='x')

        self.settings_summary_text = summary_text
        self.update_settings_summary()

    def update_settings_summary(self):
        """Update the settings summary display."""
        if not hasattr(self, 'settings_summary_text'):
            return

        summary = f"""📁 Default EXE Output: {self.default_settings['default_output_dir']}
🎨 Default Icon Output: {self.default_settings['default_icon_output_dir']}
🎯 Auto-select Icons: {'Yes' if self.default_settings['auto_select_created_icons'] else 'No'}
🔔 Show Notifications: {'Yes' if self.default_settings['show_icon_notifications'] else 'No'}
🌙 Window Transparency: {self.default_settings['window_transparency']:.0%}
🔍 Auto-search Icons: {'Yes' if self.default_settings.get('auto_search_icons', False) else 'No'}
✅ Validate Before Convert: {'Yes' if self.default_settings.get('validate_before_convert', True) else 'No'}"""

        self.settings_summary_text.config(state=tk.NORMAL)
        self.settings_summary_text.delete(1.0, tk.END)
        self.settings_summary_text.insert(1.0, summary)
        self.settings_summary_text.config(state=tk.DISABLED)

    def browse_default_exe_dir(self):
        """Browse for default EXE output directory."""
        directory = filedialog.askdirectory(title="Select Default EXE Output Directory",
                                           initialdir=self.default_exe_dir_var.get())
        if directory:
            self.default_exe_dir_var.set(directory)
            self.default_settings['default_output_dir'] = directory
            self.update_settings_summary()
            if hasattr(self, 'log_output'):
                self.log_output(f"Updated default EXE output directory: {directory}", "info")

    def browse_default_icon_dir(self):
        """Browse for default icon output directory."""
        directory = filedialog.askdirectory(title="Select Default Icon Output Directory",
                                           initialdir=self.default_icon_dir_var.get())
        if directory:
            self.default_icon_dir_var.set(directory)
            self.default_settings['default_icon_output_dir'] = directory
            self.update_settings_summary()
            if hasattr(self, 'log_output'):
                self.log_output(f"Updated default icon output directory: {directory}", "info")

    def update_transparency(self, value):
        """Update window transparency in real-time."""
        try:
            alpha = float(value)
            self.root.wm_attributes('-alpha', alpha)
            self.default_settings['window_transparency'] = alpha
            if hasattr(self, 'transparency_label'):
                self.transparency_label.config(text=f"{alpha:.0%}")
        except:
            pass

    def on_theme_changed(self, event=None):
        """Handle theme selection change."""
        if hasattr(self, 'apply_theme'):
            selected_theme = self.theme_var.get()
            self.apply_theme(selected_theme)
            if hasattr(self, 'log_output'):
                self.log_output(f"Applied {selected_theme} theme", "success")

    def save_current_settings(self):
        """Save current settings to file."""
        self.default_settings.update({
            'default_output_dir': self.default_exe_dir_var.get(),
            'default_icon_output_dir': self.default_icon_dir_var.get(),
            'auto_select_created_icons': self.auto_select_icons_var.get(),
            'show_icon_notifications': self.show_notifications_var.get(),
            'window_transparency': self.transparency_var.get(),
            'auto_search_icons': self.auto_search_icons_var.get(),
            'validate_before_convert': self.validate_before_convert_var.get()
        })

        if hasattr(self, 'theme_var'):
            self.default_settings['theme'] = self.theme_var.get()

        self.save_settings()
        self.update_settings_summary()
        self.settings_status_label.config(text="✅ Settings saved successfully!",
                                         fg=self.colors['success'])

        # Reset status message after 3 seconds
        self.root.after(3000, lambda: self.settings_status_label.config(
            text="💡 Settings are automatically applied when changed",
            fg=self.colors['fg']))

    def reset_to_defaults(self):
        """Reset all settings to default values."""
        result = messagebox.askyesno("Reset Settings",
                                   "Are you sure you want to reset all settings to default values?\n\n" +
                                   "This action cannot be undone.")
        if not result:
            return

        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

        self.default_exe_dir_var.set(desktop_path)
        self.default_icon_dir_var.set(desktop_path)
        self.auto_select_icons_var.set(True)
        self.show_notifications_var.set(True)
        self.transparency_var.set(0.95)
        self.auto_search_icons_var.set(False)
        self.validate_before_convert_var.set(True)

        if hasattr(self, 'theme_var'):
            self.theme_var.set('dark')
            if hasattr(self, 'apply_theme'):
                self.apply_theme('dark')

        self.update_transparency(0.95)

        # Update default settings
        self.default_settings.update({
            'default_output_dir': desktop_path,
            'default_icon_output_dir': desktop_path,
            'auto_select_created_icons': True,
            'show_icon_notifications': True,
            'window_transparency': 0.95,
            'auto_search_icons': False,
            'validate_before_convert': True,
            'theme': 'dark'
        })

        self.update_settings_summary()

        if hasattr(self, 'log_output'):
            self.log_output("Settings reset to defaults", "warning")

        self.settings_status_label.config(text="🔄 Settings reset to defaults!",
                                         fg=self.colors['warning'])

        # Reset status message after 3 seconds
        self.root.after(3000, lambda: self.settings_status_label.config(
            text="💡 Settings are automatically applied when changed",
            fg=self.colors['fg']))

    def apply_settings_changes(self):
        """Apply current settings without saving to file."""
        # Update output directories in converter tab if it exists
        if hasattr(self, 'output_entry'):
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, self.default_exe_dir_var.get())

        if hasattr(self, 'search_entry'):
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, self.default_icon_dir_var.get())

        # Apply behavior settings
        self.default_settings.update({
            'auto_select_created_icons': self.auto_select_icons_var.get(),
            'show_icon_notifications': self.show_notifications_var.get(),
            'auto_search_icons': self.auto_search_icons_var.get(),
            'validate_before_convert': self.validate_before_convert_var.get()
        })

        self.update_settings_summary()

        if hasattr(self, 'log_output'):
            self.log_output("Settings applied", "success")

        self.settings_status_label.config(text="✅ Settings applied successfully!",
                                         fg=self.colors['success'])

        # Reset status message after 3 seconds
        self.root.after(3000, lambda: self.settings_status_label.config(
            text="💡 Settings are automatically applied when changed",
            fg=self.colors['fg']))

    def run(self):
        """Start the application main loop."""
        try:
            # Center the window
            self.root.update_idletasks()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f'{width}x{height}+{x}+{y}')

            # Start the main loop
            self.root.mainloop()
        except KeyboardInterrupt:
            self.log_output("Application interrupted by user", "warning")
        except Exception as e:
            self.log_output(f"Application error: {e}", "error")
            messagebox.showerror("Application Error", f"An unexpected error occurred: {e}")


def main():
    """Main function to run the application."""
    try:
        app = ModernPy2ExeConverter()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        messagebox.showerror("Startup Error", f"Failed to start application: {e}")


if __name__ == "__main__":
    main()
