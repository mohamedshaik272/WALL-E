from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class MenuItem(QWidget):
    def __init__(self, icon, text, shortcut, font_family, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(10)
        
        icon_label = QLabel(icon)
        self.text_label = QLabel(text)
        self.shortcut_label = QLabel(shortcut)
        
        font = QFont(font_family, 14)
        self.text_label.setFont(font)
        self.shortcut_label.setFont(font)
        
        self.text_label.setObjectName("text_label")
        self.shortcut_label.setObjectName("shortcut_label")
        
        layout.addWidget(icon_label)
        layout.addWidget(self.text_label)
        layout.addStretch()
        layout.addWidget(self.shortcut_label)

        self.setStyleSheet("""
            QLabel {
                color: #a9b1d6;
            }
            QLabel#shortcut_label {
                color: #565f89;
            }
        """)

class MainMenu(QWidget):
    def __init__(self, parent=None, font_family="Arial"):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.font_family = font_family
        
        self.create_menu_items()
    
    def create_menu_items(self):
        menu_options = [
            ("    ", "Find File", "f    "),
            ("    ", "Projects", "p    "),
            ("    ", "Recent files", "r    "),
            ("    ", "Find Text", "t    "),
            ("    ", "Configuration", "c    "),
            ("    ", "Quit", "q    ")
        ]
        
        for icon, text, shortcut in menu_options:
            item = MenuItem(icon, text, shortcut, self.font_family, self)
            self.layout.addWidget(item)