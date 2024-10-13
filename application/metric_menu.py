from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import psutil
import time

class MenuItem(QWidget):
    def __init__(self, icon, text, shortcut, font_family, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(5)
        
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

    def update_shortcut(self, new_shortcut):
        self.shortcut_label.setText(new_shortcut)

class MetricMenu(QWidget):
    def __init__(self, parent=None, font_family="Arial"):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.font_family = font_family
        
        # Store references to menu items for updating
        self.menu_items = {}
        
        self.create_menu_items()
        self.start_update_timer()

    def create_menu_items(self):
        # Initial placeholders for the menu items
        menu_options = [
            ("    🖥️", "CPU Usage", "0.0%    "),
            ("    💽", "Disk Usage", "0.0%    "),
            ("    🗃️", "Memory Usage", "0.0%    "),
            ("    📤", "Bytes Sent", "0.00 MB    "),
            ("    📨", "Bytes Received", "0.00 MB    ")
        ]
        
        for icon, text, shortcut in menu_options:
            item = MenuItem(icon, text, shortcut, self.font_family, self)
            self.layout.addWidget(item)
            self.menu_items[text] = item  # Store reference for updating later

    def start_update_timer(self):
        # Create a QTimer to update the metrics every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(1000)  # 1000 milliseconds = 1 second

    def update_metrics(self):
        # Gather updated system metrics
        cpu_usage = psutil.cpu_percent(interval=0)  # interval=0 for non-blocking
        disk_usage = psutil.disk_usage('/').percent
        memory_usage = psutil.virtual_memory().percent
        net_io = psutil.net_io_counters()
        bytes_sent = net_io.bytes_sent / (1024 ** 2)  # Convert to MB
        bytes_received = net_io.bytes_recv / (1024 ** 2)  # Convert to MB

        # Update the corresponding menu items with new values
        self.menu_items["CPU Usage"].update_shortcut(f"{cpu_usage:.1f}%    ")
        self.menu_items["Disk Usage"].update_shortcut(f"{disk_usage:.1f}%    ")
        self.menu_items["Memory Usage"].update_shortcut(f"{memory_usage:.1f}%    ")
        self.menu_items["Bytes Sent"].update_shortcut(f"{bytes_sent:.2f} MB    ")
        self.menu_items["Bytes Received"].update_shortcut(f"{bytes_received:.2f} MB    ")