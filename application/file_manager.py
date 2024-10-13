from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from bordered_widget import BorderedWidget
from main_menu import MainMenu
from theme import Theme
from theme_buttons import ThemeButtons

class WALLEFileManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WALL-E File Manager")
        self.setGeometry(100, 100, 400, 600)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.central_widget = BorderedWidget(self)
        self.setCentralWidget(self.central_widget)

        self.setup_ui()

    def setup_ui(self):
        # WALL-E title
        self.title_label = QLabel("WALL-E")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setObjectName("logo")
        self.central_widget.content_layout.addWidget(self.title_label)

        # Add some spacing
        self.central_widget.content_layout.addSpacing(20)

        # Main Menu
        self.main_menu = MainMenu(self)
        self.central_widget.content_layout.addWidget(self.main_menu)

        self.central_widget.content_layout.addStretch(1)
        
        # Add some spacing
        self.central_widget.content_layout.addSpacing(20)
        
        # Theme Buttons
        self.theme_buttons = ThemeButtons()
        self.theme_buttons.themeChanged.connect(self.change_theme)
        self.central_widget.content_layout.addWidget(self.theme_buttons)

        self.apply_theme()

    def change_theme(self, theme):
        if theme == 'SYSTEM_LIGHT':
            Theme.set_theme(Theme.SYSTEM_LIGHT)
        elif theme == 'SYSTEM_DARK':
            Theme.set_theme(Theme.SYSTEM_DARK)
        else:
            Theme.set_theme(theme)
        self.apply_theme()

    def apply_theme(self):
        self.setStyleSheet(Theme.get_stylesheet())
        self.central_widget.update_theme()  # Update the background image
        self.update()  # Force a repaint of the entire window

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()