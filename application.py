import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLineEdit, QGridLayout, QLabel, QFileIconProvider, QScrollArea)
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath, QRegion, QIcon, QFontMetrics
from PyQt5.QtCore import Qt, QPropertyAnimation, QParallelAnimationGroup, QEasingCurve, pyqtProperty, QSize, QRectF, QPoint, QFileInfo

class ThemeIcon(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 40)
        self._rotation = 0
        self._color_t = 0  # For color interpolation

    def _set_rotation(self, rotation):
        self._rotation = rotation
        self.update()

    def _get_rotation(self):
        return self._rotation

    rotation = pyqtProperty(float, _get_rotation, _set_rotation)

    def _set_color_t(self, t):
        self._color_t = t
        self.update()

    def _get_color_t(self):
        return self._color_t

    color_t = pyqtProperty(float, _get_color_t, _set_color_t)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(20, 20)
        painter.rotate(self._rotation)
        painter.translate(-20, -20)

        # Interpolate colors
        dark_color = QColor(40, 40, 80)
        light_color = QColor(255, 165, 0)
        current_color = QColor(
            int(dark_color.red() * (1 - self._color_t) + light_color.red() * self._color_t),
            int(dark_color.green() * (1 - self._color_t) + light_color.green() * self._color_t),
            int(dark_color.blue() * (1 - self._color_t) + light_color.blue() * self._color_t)
        )

        # Draw the circle
        painter.setPen(Qt.NoPen)
        painter.setBrush(current_color)
        painter.drawEllipse(QRectF(2, 2, 36, 36))

        # Draw the half circle
        painter.setBrush(QColor(255, 255, 255, int(255 * (1 - self._color_t))))
        painter.drawChord(QRectF(2, 2, 36, 36), 90 * 16, 180 * 16)

        # Draw the rays
        painter.setPen(QPen(QColor(255, 255, 255, int(255 * (1 - self._color_t))), 2))
        for i in range(8):
            angle = i * 45
            painter.save()
            painter.translate(20, 20)
            painter.rotate(angle)
            painter.drawLine(18, 0, 22, 0)
            painter.restore()

class AnimatedButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 50)
        self.theme_icon = ThemeIcon(self)
        self.theme_icon.move(5, 5)  # Center the icon in the button
        self.is_cyberpunk = True
        self.clicked.connect(self.animate)

    def animate(self):
        self.rotation_anim = QPropertyAnimation(self.theme_icon, b"rotation")
        self.rotation_anim.setDuration(500)
        self.rotation_anim.setEasingCurve(QEasingCurve.InOutQuad)

        self.color_anim = QPropertyAnimation(self.theme_icon, b"color_t")
        self.color_anim.setDuration(500)
        self.color_anim.setEasingCurve(QEasingCurve.InOutQuad)

        if self.is_cyberpunk:
            self.rotation_anim.setStartValue(0)
            self.rotation_anim.setEndValue(180)
            self.color_anim.setStartValue(0)
            self.color_anim.setEndValue(1)
        else:
            self.rotation_anim.setStartValue(180)
            self.rotation_anim.setEndValue(360)
            self.color_anim.setStartValue(1)
            self.color_anim.setEndValue(0)

        self.anim_group = QParallelAnimationGroup()
        self.anim_group.addAnimation(self.rotation_anim)
        self.anim_group.addAnimation(self.color_anim)
        self.anim_group.start()

        self.is_cyberpunk = not self.is_cyberpunk

class CustomBorderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.border_radius = 20
        self.border_width = 2
        self.is_cyberpunk = True
        
        self._is_resizing = False
        self._resize_direction = None
        self.resize_handle_size = 10

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Create a rounded rectangle path
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self.border_radius, self.border_radius)

        # Set the window mask
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

        # Fill the background
        if self.is_cyberpunk:
            painter.fillPath(path, QColor(26, 26, 46))
        else:
            painter.fillPath(path, QColor(240, 240, 240))

        # Draw the border
        if self.is_cyberpunk:
            painter.setPen(QPen(QColor(0, 255, 255), self.border_width))
        else:
            painter.setPen(QPen(QColor(200, 200, 200), self.border_width))
        painter.drawPath(path)

    def mousePressEvent(self, event):
        if self._is_on_resize_handle(event.pos()):
            self._is_resizing = True
            self._resize_direction = self._get_resize_direction(event.pos())
        elif event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
        event.accept()

    def mouseMoveEvent(self, event):
        if self._is_resizing:
            self._resize_window(event.globalPos())
        elif event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
        event.accept()

    def mouseReleaseEvent(self, event):
        self._is_resizing = False
        self._resize_direction = None
        event.accept()

    def _is_on_resize_handle(self, pos):
        return (pos.x() < self.resize_handle_size or 
                pos.x() > self.width() - self.resize_handle_size or
                pos.y() < self.resize_handle_size or 
                pos.y() > self.height() - self.resize_handle_size)

    def _get_resize_direction(self, pos):
        left = pos.x() < self.resize_handle_size
        right = pos.x() > self.width() - self.resize_handle_size
        top = pos.y() < self.resize_handle_size
        bottom = pos.y() > self.height() - self.resize_handle_size

        if left and top:
            return 'top-left'
        elif left and bottom:
            return 'bottom-left'
        elif right and top:
            return 'top-right'
        elif right and bottom:
            return 'bottom-right'
        elif left:
            return 'left'
        elif right:
            return 'right'
        elif top:
            return 'top'
        elif bottom:
            return 'bottom'

    def _resize_window(self, global_pos):
        new_geo = self.geometry()
        if self._resize_direction == 'left' or 'left' in self._resize_direction:
            new_geo.setLeft(global_pos.x())
        if self._resize_direction == 'top' or 'top' in self._resize_direction:
            new_geo.setTop(global_pos.y())
        if self._resize_direction == 'right' or 'right' in self._resize_direction:
            new_geo.setRight(global_pos.x())
        if self._resize_direction == 'bottom' or 'bottom' in self._resize_direction:
            new_geo.setBottom(global_pos.y())
        
        if new_geo.width() >= self.minimumWidth() and new_geo.height() >= self.minimumHeight():
            self.setGeometry(new_geo)

class FileButton(QPushButton):
    def __init__(self, name, icon, parent=None):
        super().__init__(parent)
        self.setFixedSize(100, 100)
        self.setIcon(icon)
        self.setIconSize(QSize(48, 48))
        self.setText(self.elide_text(name))
        self.setStyleSheet("""
            QPushButton {
                background-color: #16213e;
                color: #00ffff;
                border: 1px solid #00ffff;
                border-radius: 5px;
                padding: 5px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #0f3460;
            }
        """)

    def elide_text(self, text):
        metrics = QFontMetrics(self.font())
        elided_text = metrics.elidedText(text, Qt.ElideRight, self.width() - 10)
        return elided_text

class CyberpunkFileManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WALL-E File Manager")
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(400, 300)
        
        self.current_path = os.path.expanduser("~")
        self.icon_provider = QFileIconProvider()
        self.items_per_page = 20
        self.current_page = 0
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title bar
        title_bar = QHBoxLayout()
        self.title_label = QLabel("WALL-E File Manager")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ffff;")
        title_bar.addWidget(self.title_label)
        layout.addLayout(title_bar)
        
        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search files...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #16213e;
                color: #00ffff;
                border: 1px solid #00ffff;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.search_bar)
        
        # File grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.grid_layout = QGridLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.next_button)
        layout.addLayout(nav_layout)
        
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button.clicked.connect(self.next_page)
        
        self.create_file_grid()
        
        self.setLayout(layout)
        
    def create_file_grid(self):
        # Clear existing items
        for i in reversed(range(self.grid_layout.count())): 
            self.grid_layout.itemAt(i).widget().setParent(None)
        
        items = os.listdir(self.current_path)
        start_index = self.current_page * self.items_per_page
        end_index = start_index + self.items_per_page
        
        for i, item in enumerate(items[start_index:end_index]):
            full_path = os.path.join(self.current_path, item)
            icon = self.icon_provider.icon(QFileInfo(full_path))
            btn = FileButton(item, icon)
            btn.clicked.connect(lambda _, path=full_path: self.item_clicked(path))
            self.grid_layout.addWidget(btn, i // 4, i % 4)
        
        self.update_nav_buttons(len(items))
        
    def update_nav_buttons(self, total_items):
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled((self.current_page + 1) * self.items_per_page < total_items)
        
    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.create_file_grid()
            
    def next_page(self):
        self.current_page += 1
        self.create_file_grid()
        
    def item_clicked(self, path):
        if os.path.isdir(path):
            self.current_path = path
            self.current_page = 0
            self.create_file_grid()
        else:
            print(f"Opening file: {path}")
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.items_per_page = (self.width() // 110) * (self.height() // 110)
        self.create_file_grid()
    
    def apply_cyberpunk_theme(self):
        self.setStyleSheet("""
            QWidget { background-color: transparent; }
            QPushButton { 
                background-color: #16213e; color: #00ffff; 
                border: 1px solid #00ffff; border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover { background-color: #0f3460; }
            QLineEdit { 
                background-color: #16213e; color: #00ffff; 
                border: 1px solid #00ffff; border-radius: 4px;
                padding: 5px;
            }
        """)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ffff;")
    
    def apply_light_theme(self):
        self.setStyleSheet("""
            QWidget { background-color: transparent; }
            QPushButton { 
                background-color: #e0e0e0; color: #333333; 
                border: 1px solid #cccccc; border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover { background-color: #d0d0d0; }
            QLineEdit { 
                background-color: #ffffff; color: #333333; 
                border: 1px solid #cccccc; border-radius: 4px;
                padding: 5px;
            }
        """)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333333;")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CyberpunkFileManager()
    window.show()
    sys.exit(app.exec_())