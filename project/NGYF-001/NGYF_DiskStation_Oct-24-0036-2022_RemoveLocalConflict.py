from audioop import add
from cgitb import html
from cmath import sqrt
from email import utils
from email.charset import add_alias
from json import load
from sqlite3 import connect
import threading
from time import sleep, time
from tokenize import group
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
import sys
import os
import folium
from folium.features import DivIcon
import asyncio
import cv2
from mavsdk import System
from mavsdk.mission import *
from utils.droneControl import plan_route, generate_mission, mission_part, open_mavsdk_server, track_display
from utils.NGYFDetector import NGYFDetector
import nest_asyncio


init_mavsdk_server = r'"sources\mavsdk-windows-x64-release\bin\mavsdk_server_bin.exe -p 50051 serial://COM4:57600"' # 你要运行的exe文件
mission_route = []
track = []
# land_mission_Items = [[22.5912,113.9753,10,10], [22.5909, 113.9753, 5, 10], [22.5905, 113.9753, 2,7]]
# goto_test_item = [22.5909, 113.9751, 40]
# lat_deg = -1.0
# lon_deg = -1.0
# abs_alt = -1.0
# rel_alt = -1.0
# land_alt = -1.0
# threshold = 0.00020  # 阈值10m

waypoint_lists = [
    [22.5917867, 113.9752335, 80, 12, 3],
    [22.5915777, 113.9755941, 80, 12, 3],
    [22.5912497, 113.9752591, 80, 12, 3],
    [22.5909264, 113.9752896, 80, 12, 1],
    [22.5904671, 113.9752947, 80, 12, 1],
    [22.5899377, 113.9753048, 80, 12, 1],
    [22.5896097, 113.9753099, 80, 12, 3],
    [22.5892395, 113.9757920, 80, 12, 3],
    [22.5888647, 113.9753353, 80, 12, 3],
    [22.5892067, 113.9749699, 80, 12, 3],
    [22.5896097, 113.9753099, 80, 12, 3],
    [22.5899377, 113.9753048, 80, 12, 1],
    [22.5904671, 113.9752947, 80, 12, 1],
    [22.5909264, 113.9752896, 80, 12, 1],
    [22.5912497, 113.9752591, 80, 12, 3],
    [22.5915214, 113.9748887, 80, 12, 3]
]

nest_asyncio.apply()


# 调用高德地图http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}
Map = folium.Map(location=[22.5905, 113.9754],
                 max_zoom=19, 
                 zoom_start=18,
                 crs="EPSG3857",
                 control_scale=True,
                 tiles = 'OpenStreetMap',  # 使用OpenStreetMap
                 attr='default')

Map.add_child(folium.LatLngPopup())                     # 显示鼠标点击点经纬度
# Map.add_child(folium.ClickForMarker(popup='Waypoint'))  # 将鼠标点击点添加到地图上

Map.save("save_map.html")

mission_Items = generate_mission(waypoint_lists)


class MainWindow(QMainWindow):
    def __init__(self, loop, drone):
        super(QMainWindow, self).__init__()
        self.setupUi(self)
        self.loop = loop
        self.drone = drone

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(960, 1080)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.setWindowTitle('NGYF-001')
        # 新建一个QWebEngineView()对象
        self.qwebengine = QWebEngineView(self)
        # 设置网页在窗口中显示的位置和大小
        self.qwebengine.setGeometry(0, 0, 960, 930)
        self.loadMap()

        self.pushButton00 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton00.setGeometry(QtCore.QRect(0, 930, 260, 50))
        self.pushButton00.setObjectName("pushButton00")
        self.pushButton01 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton01.setGeometry(QtCore.QRect(260, 930, 260, 50))
        self.pushButton01.setObjectName("pushButton01")
        self.pushButton02 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton02.setGeometry(QtCore.QRect(520, 930, 260, 50))
        self.pushButton02.setObjectName("pushButton02")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1920, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.pushButton00.setText("刷新地图")
        self.pushButton01.setText("执行任务")
        self.pushButton02.setText("投弹")

        self.pushButton00.clicked.connect(lambda: save(self))
        self.pushButton01.clicked.connect(lambda: mission_part(self.loop, self.drone, mission_Items))
        self.pushButton02.clicked.connect(lambda:bomb_part(self.loop, self.drone))
    
    def loadMap(self):
        path = "file:\\" + os.getcwd() + "\\save_map.html"
        path = path.replace('\\', '/')
        self.qwebengine.load(QUrl(path))


def connect_plane(loop, drone):
    print('连接飞机中···')
    loop.run_until_complete(drone_connect(drone))

async def drone_connect(drone:System):
    # await drone.connect(system_address="udp://:14540")
    await drone.connect()
    print('飞机连接成功！')
    # print('设置参数中···')
    # await drone.param.set_param_float('FW_T_CLMB_MAX', 2)
    # await drone.param.set_param_float('FW_T_CLMB_R_SP', 2)
    # await drone.param.set_param_float('FW_T_SINK_MAX', 2)
    # await drone.param.set_param_float('FW_T_SINK_R_SP', 2)
    # await drone.param.set_param_float('FW_MAN_P_MAX', 30)
    # await drone.param.set_param_float('FW_MAN_R_MAX', 40)
    # await drone.param.set_param_float('FW_AIRSPD_STALL', 10)
    # await drone.param.set_param_float('FW_AIRSPD_TRIM', 13)

def save(win:MainWindow):
    global track
    try: 
        track = []
        Map.save("save_map.html")
        win.loadMap()
    except:
        print('地图刷新失败')

def camera():
    detector = NGYFDetector()
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    ret, frame = cap.read()
    print(frame.shape)
    cv2.namedWindow('imshow')
    while True:
        ret, frame = cap.read()
        print('01')
        num, pos = detector.detect(frame)
        print('02')
        if(len(num) > 0):
            print(num, pos)
        print('03')
        cv2.imshow('imshow', frame)
        print('04')
        if cv2.waitKey(10)==27:  # 等待10s，按ESC退出
            print('05')
            break
        print('01')
    print('01')
    cv2.destroyAllWindows()

if __name__ == '__main__':
    boundary = [[22.5909, 113.9757], [22.5909, 113.9750], [22.5899, 113.9757], [22.5899, 113.9750]]
    # boundary = [[22.8032, 114.2953], [22.8033, 114.2956], [22.8022, 114.2955], [22.8023, 114.2958]]

    loop = asyncio.get_event_loop()
    drone = System(mavsdk_server_address='localhost', port=50051)
    app = QApplication(sys.argv)
    win = MainWindow(loop, drone)
    win.show()
    # mavsdk_thread = threading.Thread(target=open_mavsdk_server, args=(init_mavsdk_server, )).start()
    detector_thread = threading.Thread(target=camera)
    detector_thread.start()
    # connect_plane_thread = threading.Thread(target=connect_plane, args=(loop, drone))
    # connect_plane_thread.start()
    # connect_plane_thread.join()
    # route_plan_thread = threading.Thread(target=plan_route, args=(boundary, Map, mission_route, waypoint_lists))
    # route_plan_thread.start()
    # route_plan_thread.join()
    # track_display_thread = threading.Thread(target=track_display, args=(loop, drone, track, Map))
    # track_display_thread.start()
    sys.exit(app.exec_())