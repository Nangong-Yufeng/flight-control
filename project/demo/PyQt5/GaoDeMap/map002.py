from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
import sys
import os
import folium

# 调用高德地图http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}
Map = folium.Map(location=[22.5907, 113.9623],
                 zoom_start=16,
                 control_scale=True,
                 tiles='http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}',
                 attr='default')

Map.add_child(folium.LatLngPopup())                     # 显示鼠标点击点经纬度
Map.add_child(folium.ClickForMarker(popup='Waypoint'))  # 将鼠标点击点添加到地图上

# 标记一个实心圆
folium.CircleMarker(
    location=[22.5907, 113.9623],
    radius=1,
    popup='popup',
    color='#DC143C',      # 圈的颜色
    fill=True,
    fill_color='#6495E'  # 填充颜色
).add_to(Map)
Map.save("save_map.html")


class MainWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.setWindowTitle('地图显示')
        self.resize(1000, 640)
        # 新建一个QWebEngineView()对象
        self.qwebengine = QWebEngineView(self)
        # 设置网页在窗口中显示的位置和大小
        self.qwebengine.setGeometry(20, 20, 960, 600)
        # 在QWebEngineView中加载网址
        path = "file:\\" + os.getcwd() + "\\save_map.html"
        path = path.replace('\\', '/')
        self.qwebengine.load(QUrl(path))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
