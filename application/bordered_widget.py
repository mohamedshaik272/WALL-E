from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtGui import QPainter, QColor, QPen, QPixmap, QPainterPath
from PyQt5.QtCore import Qt, QRectF
from theme import Theme
import os

class BorderedWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 600)
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(20, 20, 20, 20)

        self.background_image = None
        self.load_background_image()

    def load_background_image(self):
        if Theme.get_current_background():
            image_path = os.path.join(os.path.dirname(__file__), Theme.get_current_background())
            self.background_image = QPixmap(image_path)
            if self.background_image.isNull():
                print(f"Error: Background image could not be loaded: {image_path}")
        else:
            self.background_image = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fill background
        painter.fillRect(self.rect(), QColor(Theme.COLORS[Theme.get_current_theme()]['background']))

        # Draw the background image for cyberpunk theme
        if self.background_image and not self.background_image.isNull():
            painter.drawPixmap(self.rect(), self.background_image, self.background_image.rect())

        # Draw rounded rectangle border
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()).adjusted(1, 1, -1, -1), 20, 20)
        
        border_color = QColor(Theme.COLORS[Theme.get_current_theme()]['border'])
        painter.setPen(QPen(border_color, 2))
        painter.drawPath(path)

    def update_theme(self):
        self.load_background_image()
        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)