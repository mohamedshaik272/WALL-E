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
    MENU_FONT = "Segoe UI"

    # Color schemes
    COLORS = {
        SYSTEM_LIGHT: {
            "background": "#f0f0f0",
            "text": "#333333",
            "accent": "#333333",
            "border": "#d0d0d0",
        },
        SYSTEM_DARK: {
            "background": "#2d2d2d",
            "text": "#ffffff",
            "accent": "#ffffff",
            "border": "#555555",
        },
        CYBERPUNK: {
            "background": "transparent",
            "text": "#ffffff",
            "accent": "#4fc8b7",
            "border": "#4fc8b7",
        }
    }

    @classmethod
    def initialize(cls):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Load cyberpunk fonts
        cyberpunk_title_font_path = os.path.join(current_dir, "ForceBattle.otf")
        cyberpunk_title_font_id = QFontDatabase.addApplicationFont(cyberpunk_title_font_path)
        if cyberpunk_title_font_id != -1:
            cls.CYBERPUNK_TITLE_FONT = QFontDatabase.applicationFontFamilies(cyberpunk_title_font_id)[0]
        else:
            cls.CYBERPUNK_TITLE_FONT = "Arial"

        cyberpunk_menu_font_path = os.path.join(current_dir, "PrimaSansMonoBT-Roman.otf")
        cyberpunk_menu_font_id = QFontDatabase.addApplicationFont(cyberpunk_menu_font_path)
        if cyberpunk_menu_font_id != -1:
            cls.CYBERPUNK_MENU_FONT = QFontDatabase.applicationFontFamilies(cyberpunk_menu_font_id)[0]
        else:
            cls.CYBERPUNK_MENU_FONT = "Courier"

        # Load custom font for light and dark modes
        normal_title_font_path = os.path.join(current_dir, "LemonMilkMedium.otf")  # Replace with your actual font file name
        normal_title_font_id = QFontDatabase.addApplicationFont(normal_title_font_path)
        if normal_title_font_id != -1:
            cls.NORMAL_TITLE_FONT = QFontDatabase.applicationFontFamilies(normal_title_font_id)[0]
            cls.TITLE_FONT = cls.NORMAL_TITLE_FONT
        else:
            cls.CYBERPUNK_TITLE_FONT = "Arial"
            
        # Load custom font for light and dark modes
        normal_menu_font_path = os.path.join(current_dir, "LemonMilkLight.otf")  # Replace with your actual font file name
        normal_menu_font_id = QFontDatabase.addApplicationFont(normal_menu_font_path)
        if normal_menu_font_id != -1:
            cls.NORMAL_MENU_FONT = QFontDatabase.applicationFontFamilies(normal_menu_font_id)[0]
            cls.MENU_FONT = cls.NORMAL_MENU_FONT
        else:
            cls.CYBERPUNK_MENU_FONT = "Courier"


    @classmethod
    def get_stylesheet(cls):
        colors = cls.COLORS[cls.current_theme]
        
        if cls.current_theme == cls.CYBERPUNK:
            title_font = cls.CYBERPUNK_TITLE_FONT
            menu_font = cls.CYBERPUNK_MENU_FONT
        else:
            title_font = cls.TITLE_FONT
            menu_font = cls.MENU_FONT
        
        return f"""
            QWidget {{
                background-color: {colors['background']};
                color: {colors['text']};
                font-family: "{menu_font}";
                font-size: 14px;
            }}
            QLabel#logo {{
                color: {colors['accent']};
                font-size: 48px;
                font-weight: bold;
                font-family: "{title_font}";
            }}
            QLabel#menu-item {{
                color: {colors['text']};
                font-size: 18px;
                font-family: "{menu_font}";
            }}
            QLabel#menu-shortcut {{
                color: {colors['accent']};
                font-size: 18px;
                font-family: "{menu_font}";
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
            if theme_name == cls.CYBERPUNK:
                cls.current_background = f"night-{cls.COLORS[theme_name]['accent'][1:]}.png"
            else:
                cls.current_background = None
        else:
            cls.current_theme = cls.CYBERPUNK
            color = theme_name.lstrip('#')
            cls.COLORS[cls.CYBERPUNK]['accent'] = theme_name
            cls.COLORS[cls.CYBERPUNK]['border'] = theme_name
            cls.current_background = f"night-{color}.png"

    @classmethod
    def get_current_background(cls):
        return cls.current_background

    @classmethod
    def get_current_theme(cls):
        return cls.current_theme