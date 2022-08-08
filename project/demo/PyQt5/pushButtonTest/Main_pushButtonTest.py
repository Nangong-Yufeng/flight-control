import sys
from PyQt5.QtWidgets import QMainWindow,QApplication,QWidget, QDialog, QDockWidget
from Ui_pushButtonTest import Ui_DockWidget

class My_Ui_pushButton(QDockWidget, Ui_DockWidget):
    def __init__(self, parent = None):
        super(My_Ui_pushButton, self).__init__(parent)
        self.setupUi(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_Ui_pushButton = My_Ui_pushButton()
    my_Ui_pushButton.show()
    sys.exit(app.exec_())    