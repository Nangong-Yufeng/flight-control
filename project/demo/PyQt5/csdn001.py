import PyQt5
from PyQt5.Qt import *
import sys


class Window(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowFlags(Qt.FramelessWindowHint)  # 取消窗体标题栏
        self.setWindowOpacity(0.9)  # 设置窗体透明度
        # 2.2设置控件
        self.setWindowTitle("顶层窗口操作-案例")
        self.resize(500, 500)
        self.btn_w = 80
        self.btn_h = 40
        self.top_margin = 0
        self.setup_ui()

    def setup_ui(self):
        close_btn = QPushButton(self)
        self.close_btn = close_btn
        close_btn.setText("关闭")
        close_btn.resize(self.btn_w, self.btn_h)

        max_btn = QPushButton(self)
        self.max_btn = max_btn
        max_btn.setText("最大化")
        max_btn.resize(self.btn_w, self.btn_h)

        min_but = QPushButton(self)
        self.min_but = min_but
        min_but.setText("最小化")
        min_but.resize(self.btn_w, self.btn_h)

        def max_mormal():
            if self.isMaximized():
                self.showNormal()
                max_btn.setText("最大化")
            else:
                self.showMaximized()
                max_btn.setText("恢复")

        # 按钮功能
        close_btn.pressed.connect(self.close)
        max_btn.pressed.connect(max_mormal)
        min_but.pressed.connect(self.showMinimized)

    def resizeEvent(self, QResizeEvent):
        close_btn_x = self.width() - self.btn_w
        close_btn_y = self.top_margin
        self.close_btn.move(close_btn_x, close_btn_y)

        max_btn_x = close_btn_x - self.btn_w
        max_but_y = self.top_margin
        self.max_btn.move(max_btn_x, max_but_y)

        min_but_x = max_btn_x - self.btn_w
        min_but_y = self.top_margin
        self.min_but.move(min_but_x, min_but_y)

    def mousePressEvent(self, evt):  # 鼠标执行
        if evt.button() == Qt.LeftButton:  # 判断是否为左键执行
            self.Flag = True
            self.mouse_x = evt.globalX()
            self.mouse_y = evt.globalY()
            self.origin_x = self.x()
            self.origin_y = self.y()

    def mouseMoveEvent(self, evt):  # 鼠标移动
        if self.Flag == True:
            move_x = evt.globalX() - self.mouse_x
            move_y = evt.globalY() - self.mouse_y
            dest_x = self.origin_x + move_x
            dest_y = self.origin_y + move_y
            self.move(dest_x, dest_y)

    def mouseReleaseEvent(self, QMouseEvent):  # 鼠标释放
        self.Flag = False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
