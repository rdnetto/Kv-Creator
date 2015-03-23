
from PySide.QtGui import QMainWindow
from creator_ui import Ui_MainWindow


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

