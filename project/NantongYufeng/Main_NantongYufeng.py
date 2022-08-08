import sys
from PyQt5.QtWidgets import QMainWindow,QApplication,QWidget, QDialog, QDockWidget
from Ui_NantongYufeng import Ui_MainWindow

# class My_MainWindow(QMainWindow, Ui_MainWindow):
#     def __init__(self, parent = None):
#         super(My_MainWindow, self).__init__(parent)
#         self.setupUi(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_MainWindow = Ui_MainWindow()
    my_MainWindow.setupUi(my_MainWindow)
    my_MainWindow.show()
    sys.exit(app.exec_())