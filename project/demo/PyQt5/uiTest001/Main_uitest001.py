import sys
from PyQt5.QtWidgets import QMainWindow,QApplication,QWidget, QDialog
from Ui_uitest001 import Ui_Dialog  #导入你写的界面类
 
 
class MyUi_Dialog(QDialog,Ui_Dialog): #这里也要记得改
    def __init__(self,parent =None):
        super(MyUi_Dialog,self).__init__(parent)
        self.setupUi(self)
 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myUi_D = MyUi_Dialog()
    myUi_D.show()
    sys.exit(app.exec_())    