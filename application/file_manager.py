from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QWidget, QApplication, QShortcut
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QPixmap, QPainterPath, QKeySequence
from bordered_widget import BorderedWidget
from main_menu import MainMenu
from metric_menu import MetricMenu
from theme import Theme
from theme_buttons import ThemeButtons

class WALLEFileManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WALL-E File Manager")
        self.setGeometry(100, 100, 400, 600)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        
        self.central_widget = BorderedWidget(self)
        self.setCentralWidget(self.central_widget)

        self.setup_ui()
        self.setup_shortcuts()

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
        self.main_menu.item_clicked.connect(self.handle_menu_click)
        self.central_widget.content_layout.addWidget(self.main_menu)
        
        # Add some spacing
        self.central_widget.content_layout.addSpacing(20)
        
        # Live Metrics title
        self.title_label = QLabel("Live Metrics")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.central_widget.content_layout.addWidget(self.title_label)
        
        # Metric Menu
        self.metric_menu = MetricMenu(self)
        self.central_widget.content_layout.addWidget(self.metric_menu)

        self.central_widget.content_layout.addStretch(1)
        
        # Add some spacing
        self.central_widget.content_layout.addSpacing(20)
        
        # Theme Buttons
        self.theme_buttons = ThemeButtons()
        self.theme_buttons.themeChanged.connect(self.change_theme)
        self.central_widget.content_layout.addWidget(self.theme_buttons)

        self.apply_theme()
        
    def setup_shortcuts(self):
        shortcuts = [
            ('d', "Organize Directory"),
            ('r', "Organize Drive"),
            ('c', "Clean-Up"),
            ('f', "Find Files"),
            ('g', "Configuration"),
            ('q', "Quit")
        ]

        for key, description in shortcuts:
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(self.quit_application)

    
    def handle_menu_click(self, item_text):
        print(f"Clicked: {item_text}")
        # For now, all menu items will quit the application
        self.quit_application()

    def quit_application(self):
        QApplication.quit()
    
    def change_theme(self, theme):
        if theme == 'SYSTEM_LIGHT':
            Theme.set_theme(Theme.SYSTEM_LIGHT)
        elif theme == 'SYSTEM_DARK':
            Theme.set_theme(Theme.SYSTEM_DARK)
        else:
            Theme.set_theme(theme)
        self.apply_theme()

    def apply_theme(self):
        stylesheet = Theme.get_stylesheet()
        self.setStyleSheet(stylesheet)
        self.central_widget.setStyleSheet(stylesheet)
        self.main_menu.setStyleSheet(stylesheet)
        self.metric_menu.setStyleSheet(stylesheet)
        
        if Theme.get_current_theme() == Theme.CYBERPUNK:
            self.setAttribute(Qt.WA_TranslucentBackground, True)
        else:
            self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        self.central_widget.update_theme()
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.quit_application()
        else:
            super().keyPressEvent(event)