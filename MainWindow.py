
from threading import Thread
from PySide.QtGui import QMainWindow
from creator_ui import Ui_MainWindow

import kivy.app
import kivy.lang


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.demoThread = None
        self.actionOpen.triggered.connect(self.openFile)


    def openFile(self):
        if(self.demoThread is None or not self.demoThread.is_alive()):
            self.demoThread = Thread(target=demo)
            self.demoThread.daemon = True
            self.demoThread.start()


def demo():
    '''Event loop for demo application'''

    def _build():
        return kivy.lang.Builder.load_file("test.kv")

    app = kivy.app.App()
    app.build = _build
    app.run()

