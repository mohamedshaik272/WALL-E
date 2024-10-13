import os
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtWidgets import QApplication

class Theme:
    # Theme names
    SYSTEM_LIGHT = "System Light"
    SYSTEM_DARK = "System Dark"
    CYBERPUNK = "Cyberpunk"

    # Current theme
    current_theme = CYBERPUNK
    current_background = "night-4fc8b7.png"

    # Default fonts
    TITLE_FONT = "Arial"
    MENU_FONT = "Courier"

    # Color schemes
    COLORS = {
        SYSTEM_LIGHT: {
            "background": "#ffffff",
            "text": "#000000",
            "accent": "#000000",
        },
        SYSTEM_DARK: {
            "background": "000000",
            "text": "#ffffff",
            "accent": "#ffffff",
        },
        CYBERPUNK: {
            "background": "transparent",
            "text": "#ffffff",
            "accent": "#4fc8b7",
        }
    }

    @classmethod
    def initialize(cls):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Load title font
        title_font_path = os.path.join(current_dir, "ForceBattle.otf")
        title_font_id = QFontDatabase.addApplicationFont(title_font_path)
        if title_font_id != -1:
            cls.TITLE_FONT = QFontDatabase.applicationFontFamilies(title_font_id)[0]
            print(f"Loaded title font: {cls.TITLE_FONT}")
        else:
            print(f"Failed to load title font from {title_font_path}")
            cls.TITLE_FONT = "Arial"

        # Load menu font
        menu_font_path = os.path.join(current_dir, "PrimaSansMonoBT-Roman.otf")
        menu_font_id = QFontDatabase.addApplicationFont(menu_font_path)
        if menu_font_id != -1:
            cls.MENU_FONT = QFontDatabase.applicationFontFamilies(menu_font_id)[0]
            print(f"Loaded menu font: {cls.MENU_FONT}")
        else:
            print(f"Failed to load menu font from {menu_font_path}")
            cls.MENU_FONT = "Courier"

    @classmethod
    def get_stylesheet(cls):
        colors = cls.COLORS[cls.current_theme]
        
        return f"""
            QWidget {{
                background-color: {colors['background']};
                color: {colors['accent']};
                font-family: "{cls.MENU_FONT}";
                font-size: 14px;
            }}
            QLabel#logo {{
                color: {colors['accent']};
                font-size: 48px;
                font-weight: bold;
                font-family: "{cls.TITLE_FONT}";
            }}
            QLabel#menu-item {{
                color: {colors['text']};
                font-size: 18px;
                font-family: "{cls.MENU_FONT}";
            }}
            QLabel#menu-shortcut {{
                color: {colors['text']};
                font-size: 18px;
                font-family: "{cls.MENU_FONT}";
            }}
            CircularButton {{
                border: none;
                border-radius: 15px;
            }}
            CircularButton:hover {{
                border: 2px solid {colors['accent']};
            }}
        """

    @classmethod
    def set_theme(cls, theme_name):
        if theme_name in [cls.SYSTEM_LIGHT, cls.SYSTEM_DARK, cls.CYBERPUNK]:
            cls.current_theme = theme_name
            cls.current_background = f"night-{cls.COLORS[theme_name]['accent'][1:]}.png"
        else:
            cls.current_theme = cls.CYBERPUNK
            color = theme_name.lstrip('#')
            cls.COLORS[cls.CYBERPUNK]['accent'] = theme_name
            cls.COLORS[cls.CYBERPUNK]['text'] = theme_name
            cls.current_background = f"night-{color}.png"

    @classmethod
    def get_current_background(cls):
        return cls.current_background

    @classmethod
    def get_current_theme(cls):
        return cls.current_theme