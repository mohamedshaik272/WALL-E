from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt

class MenuItem(QWidget):
    def __init__(self, text, shortcut, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        
        self.text_label = QLabel(text, self)
        self.text_label.setObjectName("menu-item")
        self.shortcut_label = QLabel(shortcut, self)
        self.shortcut_label.setObjectName("menu-shortcut")
        
        self.layout.addWidget(self.text_label)
        self.layout.addStretch()
        self.layout.addWidget(self.shortcut_label)