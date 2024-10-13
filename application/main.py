import sys
from PyQt5.QtWidgets import QApplication
from file_manager import WALLEFileManager
from theme import Theme

def main():
    app = QApplication(sys.argv)
    
    # Initialize the theme
    Theme.initialize()
    
    walle_manager = WALLEFileManager()
    walle_manager.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()