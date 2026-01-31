import tkinter as tk
import os
import json
from unittest.mock import MagicMock

class MockApp:
    def __init__(self):
        self.root = MagicMock()
        self.setup_theme_system()
        # Removed the redundant block here
        self.setup_styles()

    def setup_theme_system(self):
        desktop_path = "mock_desktop"
        self.default_settings = {
            'font_size': 12,
            'theme': 'dark'
        }
        self.load_settings = MagicMock()
        self.init_color_scheme = MagicMock()
        self.colors = {'bg': 'black', 'fg': 'white', 'card': 'gray', 'surface': 'lightgray', 'accent': 'blue', 'accent_hover': 'lightblue', 'success': 'green', 'warning': 'orange', 'error': 'red', 'border': 'darkgray'}

    def setup_styles(self):
        print(f"Default settings in setup_styles: {self.default_settings}")
        self.base_font_size = self.default_settings.get('font_size', 10)
        print(f"Base font size: {self.base_font_size}")

app = MockApp()
