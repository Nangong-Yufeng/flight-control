import threading
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
import sys
import os
import folium

# 调用高德地图http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}
Map = folium.Map(location=[22.590719999999997, 113.97554149999999],
                 max_zoom=19, 
                 zoom_start=18,
                 crs="EPSG3857", 
                 control_scale=True,
                 tiles = 'OpenStreetMap',  # 使用OpenStreetMap
                 attr='default')

Map.add_child(folium.LatLngPopup())                     # 显示鼠标点击点经纬度
# Map.add_child(folium.ClickForMarker(popup='Waypoint'))  # 将鼠标点击点添加到地图上

# 标记一个实心圆
folium.CircleMarker(
    location=[22.590719999999997, 113.97554149999999],
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
        self.resize(1920, 1080)
        # 新建一个QWebEngineView()对象
        self.qwebengine = QWebEngineView(self)
        # 设置网页在窗口中显示的位置和大小
        self.qwebengine.setGeometry(0, 0, 1920, 1080)
        # 在QWebEngineView中加载网址
        path = "file:\\/" + os.getcwd() + "\\save_map.html"
        path = path.replace('\\', '/')
        self.qwebengine.load(QUrl(path))


def route_plan(boundary, win):  # 默认给出四点边界
    


if __name__ == '__main__':
    boundary = [[22.5908, 113.9757], [22.5908, 113.9750], [22.5899, 113.9757], [22.5899, 113.9750]]
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    threading.Thread(target=route_plan, args=(boundary, win)).start()
    sys.exit(app.exec_())

