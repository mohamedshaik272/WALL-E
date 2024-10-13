from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QBrush

class CircularButton(QPushButton):
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.setFixedSize(15, 15)
        self.color = QColor(color)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(self.color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.rect())

class ThemeButtons(QWidget):
    themeChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setSpacing(10)

        colors = ['#000000', '#4fc8b7', '#e696a6', '#d2ad68', '#76adbc', '#b0a3d0', '#ffffff']
        for color in colors:
            button = CircularButton(color)
            button.clicked.connect(lambda checked, c=color: self.on_button_clicked(c))
            layout.addWidget(button)

        self.setLayout(layout)

    def on_button_clicked(self, color):
        if color == '#ffffff':
            self.themeChanged.emit('SYSTEM_LIGHT')
        elif color == '#000000':
            self.themeChanged.emit('SYSTEM_DARK')
        else:
            self.themeChanged.emit(color)