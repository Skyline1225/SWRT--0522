import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from config import Settings

def main():
    Settings.ensure_dirs()

    app = QApplication(sys.argv)
    app.setApplicationName('SWRT文档内容更新软件')
    try:
        app.setApplicationDisplayName('SWRT文档内容更新软件')
    except Exception:
        pass

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
