from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class MenuItem(QWidget):
    clicked = pyqtSignal(str)  # Signal to emit when clicked

    def __init__(self, icon, text, shortcut, font_family, parent=None):
        super().__init__(parent)
        self.text = text
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
                color: #ffffff;
            }
            QLabel#shortcut_label {
                color: #ffffff;
            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.text)
        super().mousePressEvent(event)

class MainMenu(QWidget):
    item_clicked = pyqtSignal(str)  # Signal to emit when any item is clicked

    def __init__(self, parent=None, font_family="Arial"):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.font_family = font_family
        
        self.create_menu_items()
    
    def create_menu_items(self):
        menu_options = [
            ("    📂", "Organize Directory", "d    "),
            ("    🗄️", "Organize Drive", "r    "),
            ("    🧹", "Clean-Up", "c    "),
            ("    🔎", "Find Files", "f    "),
            ("    🛠️", "Configuration", "g    "),
            ("    ❌", "Quit", "q    ")
        ]
        
        for icon, text, shortcut in menu_options:
            item = MenuItem(icon, text, shortcut, self.font_family, self)
            item.clicked.connect(self.on_item_clicked)
            self.layout.addWidget(item)

    def on_item_clicked(self, text):
        self.item_clicked.emit(text)