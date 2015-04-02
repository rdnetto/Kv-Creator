
import kivy.app
import kivy.lang
import traceback

from threading import Thread
from PySide.QtGui import QMainWindow, QMessageBox, QApplication
from Queue import Queue

from creator_ui import Ui_MainWindow
from kvparser import *


def ErrorHandler(func):
    '''Function decorator for displaying exceptions'''

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            traceback.print_exc()
            QMessageBox.critical(None, "Error", traceback.format_exc())
            QApplication.exit(1)

    return wrapper


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.demoThread = None
        self.actionOpen.triggered.connect(self.openFile)
        self.actionSave.triggered.connect(self.saveFile)


    @ErrorHandler
    def openFile(self):
        if(self.demoThread is not None and self.demoThread.is_alive()):
            raise Exception("File already open")

        # load file in kivy thread
        rootQueue = Queue()
        path = "test.kv"
        self.demoThread = Thread(name="kivy", target=demo, args=[path, rootQueue])
        self.demoThread.daemon = True
        self.demoThread.start()
        self.rootWidget = rootQueue.get()

        self.kvfile = KvFile(path)

        if(self.rootWidget is None):
            raise Exception("Failed to load file")
        else:
            self.kvfile.rootRule.populate(self.rootWidget)

        print("Parsed and corresponded kv file:")
        print("\n".join(map(str, self.kvfile.elements)))


    @ErrorHandler
    def saveFile(self):
        if(self.kvfile is None):
            raise Exception("No file open")

        self.kvfile.save()


def demo(path, rootQueue):
    '''Event loop for demo application
    path: the .kv file to load
    rootQueue: a Queue that the root widget should be pushed onto (or None if creation fails)
    '''

    def _build():
        try:
            root = kivy.lang.Builder.load_file(path)
            rootQueue.put(root)
            return root
        except:
            rootQueue.put(None)
            raise

    app = kivy.app.App()
    app.build = _build
    app.run()


