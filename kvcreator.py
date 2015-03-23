#!/usr/bin/env python2

import sys
from PySide.QtGui import QApplication
from MainWindow import MainWindow


if(__name__ == "__main__"):
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    app.exec_()

