import asyncio
import sys
from sources.MainWindow import Ui_MainWindow
from PyQt5.QtWebEngineWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    app = QApplication(sys.argv)
    my_MainWindow = Ui_MainWindow(loop)
    # my_MainWindow.setupUi(my_MainWindow)
    my_MainWindow.show()
    sys.exit(app.exec_())