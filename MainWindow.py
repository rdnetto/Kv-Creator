
import kivy.app
import kivy.lang

from threading import Thread
from PySide.QtGui import QMainWindow
from Queue import Queue

from creator_ui import Ui_MainWindow
from kvparser import parseKv


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.demoThread = None
        self.actionOpen.triggered.connect(self.openFile)


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

        if(self.rootWidget is None):
            raise Exception("Failed to load file")

        # TODO: parse Kv file, correspond to widget tree
        (self.rootRule, self.classRules) = parseKv(path)

        # TODO; populate widget tree


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


