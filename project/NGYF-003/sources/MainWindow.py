import cv2
import os
import nest_asyncio
import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg # pyqt5的画布
import matplotlib.pyplot as plt

from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from mavsdk import System
from utils.UIutils import *
from utils.DroneUtils import connect_plane, scout_mission, goto, arm, disarm, drop_bomb


nest_asyncio.apply()
main_class = uic.loadUiType("Control.ui")[0]
_translate = QtCore.QCoreApplication.translate

# class ControlWindow(QDialog):
#     def __init__(self, parent, loop, drone):
#         super(ControlWindow, self).__init__(parent)
#         control_ui = "Control.ui"
#         uic.loadUi(control_ui, self)
#         self.show()
        
#         threading.Thread(target = drone_keyboard).start()
#         print("Input keyboard")
#         loop = asyncio.get_event_loop()
#         loop.run_until_complete(manual_controls(drone))

class Ui_MainWindow(QMainWindow):
    def __init__(self, loop):
        super(QMainWindow, self).__init__()
        self.timer_video = QtCore.QTimer()
        self.loop = loop
        self.drone = System(mavsdk_server_address='localhost', port=50051) # drone on windows
        # self.drone = System() # drone on ubuntu
        self.setupUi(self)
        init_cam(self)
        self.init_slots()
        self.cap = cv2.VideoCapture()
        self.out = None
        self.targets = [] # 标靶数字
        # self.waypoint_lists = [ # 龙岗
        #     [22.8031954, 114.2962549, 30, 12, 2],
        #     [22.8037724, 114.2956346, 30, 12, 2],
        #     [22.8032220, 114.2953028, 30, 12, 2],
        #     [22.8031555, 114.2952963, 30, 12, 2],
        #     [22.8030942, 114.2953248, 30, 12, 1],
        #     [22.8029526, 114.2953549, 30, 12, 1],
        #     [22.8028139, 114.2953834, 30, 12, 1],
        #     [22.8027599, 114.2953913, 30, 12, 1],
        #     [22.8025204, 114.2954563, 30, 12, 1],
        #     [22.8023335, 114.2954863, 30, 12, 1],
        #     [22.8021671, 114.2955259, 30, 12, 1], 
        #     [22.8020401, 114.2955497, 30, 12, 1], 
        #     [22.8020172, 114.2955569, 30, 12, 1], 
        #     [22.8019363, 114.2955737, 30, 12, 1], 
        #     [22.8017915, 114.2956036, 30, 12, 1],
        #     [22.8016020, 114.2956391, 30, 12, 1]

        # ]
        # self.waypoint_lists = [ # 大学城体育场
        #     [22.5932748, 113.9751824, 80, 12, 1],
        #     [22.5930920, 113.9751824, 80, 12, 1],
        #     [22.5924288, 113.9752456, 80, 12, 1], 
        #     [22.5919720, 113.9752622, 80, 12, 1],
        #     [22.5915029, 113.9752555, 80, 12, 1], 
        #     [22.5909296, 113.9752788, 80, 12, 1],
        #     [22.5905679, 113.9753087, 80, 12, 1], 
        #     [22.5902644, 113.9753252, 80, 12, 1],
        #     [22.5899179, 113.9753087, 80, 12, 1],
        #     [22.5894244, 113.9753485, 80, 12, 1],
        #     [22.5889829, 113.9753618, 80, 12, 2],
        #     [22.5884372, 113.9753585, 80, 12, 2],
        #     [22.5881122, 113.9753319, 80, 12, 2]
        # ]
        # self.waypoint_lists = [
        #     [22.8049050, 114.2949779, 45, 12, 1],
        #     [22.8045625, 114.2951030, 50, 12, 1],
        #     [22.8038427, 114.2951826, 50, 12, 1],
        #     [22.8038427, 114.2951826, 50, 12, 1],
        #     [22.8031613, 114.2952925, 50, 12, 1],
        #     [22.8027001, 114.2954025, 50, 12, 1],
        #     [22.8020886, 114.2955314, 50, 12, 1],
        #     [22.8016413, 114.2956261, 40, 12, 1],
        #     [22.8004497, 114.2959407, 40, 12, 1], # 下端航点
        #     [22.8016413, 114.2956261, 40, 12, 1],
        #     [22.8020886, 114.2955314, 40, 12, 1],
        #     [22.8021165, 114.2955352, 30, 12, 1], # 跑道南端
        #     [22.8027001, 114.2954025, 10, 12, 1],

        #     [22.8029726, 114.2953532, 4, 12, 1],
        #     [22.8031264, 114.2953077, 4, 12, 1], # 跑道北端
        #     [22.8031613, 114.2952925, 4, 12, 1],
        #     [22.8032557, 114.2952925, 4, 12, 1],
        #     [22.8032836, 114.2952963, 4, 12, 1],
        #     [22.8034304, 114.2952812, 4, 12, 1],
        #     [22.8035806, 114.2952243, 4, 12, 1],

        #     [22.8038427, 114.2951826, 30, 12, 1],
            
        # ]
        # self.waypoint_lists = [
        #     [22.8029679, 114.2939996, 45, 12, 1],
        #     [22.8029580, 114.2945740, 45, 12, 1],
        #     [22.8030174, 114.2949229, 40, 12, 1],
        #     [22.8030570, 114.2953094, 40, 12, 1], # 跑道北端
        #     [22.8031164, 114.2956583, 40, 12, 1],
        #     [22.8031708, 114.2960717, 40, 12, 1],
        #     [22.8032401, 114.2963562, 40, 12, 1],
        #     [22.8032253, 114.2969252, 40, 12, 1], # 最东点
        #     [22.8032401, 114.2963562, 30, 12, 1],
        #     [22.8031708, 114.2960717, 20, 12, 1],
        #     [22.8031164, 114.2956583, 10, 12, 1],
        #     [22.8030570, 114.2953094, 5, 12, 1], # 跑道北端
        #     [22.8020871, 114.2955188, 40, 12, 1] # 跑道南端
        # ]
        self.waypoint_lists = [
            # [22.8067582, 114.2962184, 45, 12, 1], 
            [22.8064493, 114.2961178, 60, 12, 1],
            [22.8055896, 114.2959782, 60, 12, 1],
            [22.8048929, 114.2955671, 60, 12, 1],
            [22.8043288, 114.2956422, 60, 12, 1],
            [22.8037597, 114.2954812, 60, 12, 1],
            [22.8030570, 114.2953094, 60, 12, 1], # 跑道北端
            [22.8025875, 114.2951216, 40, 12, 1],
            [22.8022891, 114.2949955, 40, 12, 1],
            [22.8017785, 114.2948254, 40, 12, 1], 

            [22.8012859, 114.2944258, 40, 12, 1], # 最左下
            [22.8022891, 114.2949955, 30, 12, 1],
            [22.8025875, 114.2951216, 20, 12, 1],
            [22.8030570, 114.2953094, 10, 12, 1], # 跑道北端
            
            [22.8031668, 114.2954432, 10, 12, 1],
            [22.8032515, 114.2955101, 10, 12, 1],
            [22.8033363, 114.2955770, 10, 12, 1],
            [22.8041652, 114.2959103, 10, 12, 1],
            [22.8037597, 114.2954812, 40, 12, 1],
            [22.8020871, 114.2955188, 40, 12, 1] # 跑道南端
        ]



    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(2560, 1200)
        font = QtGui.QFont()
        font.setFamily("Arial") #括号里可以设置成自己想要的其它字体
        font.setPointSize(18)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        # 新建一个QWebEngineView()对象
        # self.qwebengine = QWebEngineView(self)
        # # 设置网页在窗口中显示的位置和大小
        # self.qwebengine.setGeometry(1920, 0, 640, 640)
        # # 在QWebEngineView中加载网址
        # path = "file:\\" + os.getcwd() + "\\sources/save_map.html"
        # path = path.replace('\\', '/')
        # self.qwebengine.load(QUrl(path))
        # self.centralwidget = QtWidgets.QWidget(MainWindow)
        # self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(1920, 0, 640, 640))
        self.canvas = MyMatPlotAnimation(width=5, heigh=4, dpi=100)
        plotcos(self)
        self.hboxlayout = QtWidgets.QHBoxLayout(self.label)
        self.hboxlayout.addWidget(self.canvas)
        
        self.label_vision = QtWidgets.QLabel(self.centralwidget)
        self.label_vision.setGeometry(QtCore.QRect(0, 0, 1920, 1080))
        self.label_vision.setObjectName("label_vision")

        # self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        # self.pushButton.setGeometry(QtCore.QRect(30, 610, 260, 30))
        # self.pushButton.setObjectName("pushButton")
        # self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        # self.pushButton_2.setGeometry(QtCore.QRect(350, 610, 260, 30))
        # self.pushButton_2.setObjectName("pushButton_2")
        
        self.pushButton_connect_plane = QtWidgets.QPushButton(self.centralwidget) # connect plane
        self.pushButton_connect_plane.setGeometry(QtCore.QRect(1920, 640, 320, 40))
        self.pushButton_connect_plane.setObjectName("pushButton_connect_plane")
        self.pushButton_camera = QtWidgets.QPushButton(self.centralwidget) # connect camera
        self.pushButton_camera.setGeometry(QtCore.QRect(2240, 640, 320, 40))
        self.pushButton_camera.setObjectName("pushButton_camera")
        self.pushButton_scout_mission = QtWidgets.QPushButton(self.centralwidget) # scout mission
        self.pushButton_scout_mission.setGeometry(QtCore.QRect(1920, 680, 640, 40))
        self.pushButton_scout_mission.setObjectName("pushButton_scout_mission")
        self.pushButton_goto1 = QtWidgets.QPushButton(self.centralwidget) #  goto 1
        self.pushButton_goto1.setGeometry(QtCore.QRect(1920, 720, 160, 40))
        self.pushButton_goto1.setObjectName("pushButton_goto1")
        self.pushButton_goto2 = QtWidgets.QPushButton(self.centralwidget) # goto 2
        self.pushButton_goto2.setGeometry(QtCore.QRect(2080, 720, 160, 40))
        self.pushButton_goto2.setObjectName("pushButton_goto2")
        self.pushButton_goto3 = QtWidgets.QPushButton(self.centralwidget) # goto 3
        self.pushButton_goto3.setGeometry(QtCore.QRect(2240, 720, 160, 40))
        self.pushButton_goto3.setObjectName("pushButton_goto3")
        self.pushButton_goto4 = QtWidgets.QPushButton(self.centralwidget) # goto 4
        self.pushButton_goto4.setGeometry(QtCore.QRect(2400, 720, 160, 40))
        self.pushButton_goto4.setObjectName("pushButton_goto4")
        self.pushButton_arm = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_arm.setGeometry(QtCore.QRect(1920, 760, 213, 40))
        self.pushButton_arm.setObjectName("pushButton_arm")
        self.pushButton_disarm = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_disarm.setGeometry(QtCore.QRect(2133, 760, 214, 40))
        self.pushButton_disarm.setObjectName("pushButton_disarm")
        # self.pushButton_12 = QtWidgets.QPushButton(self.centralwidget)
        # self.pushButton_12.setGeometry(QtCore.QRect(30, 860, 435, 30))
        # self.pushButton_12.setObjectName("pushButton_12")
        self.pushButton_kill = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_kill.setGeometry(QtCore.QRect(2347, 760, 213, 40))
        self.pushButton_kill.setObjectName("pushButton_kill")
        # self.pushButton_14 = QtWidgets.QPushButton(self.centralwidget)
        # self.pushButton_14.setGeometry(QtCore.QRect(30, 760, 435, 30))
        # self.pushButton_14.setObjectName("pushButton_14")
        self.pushButton_manual_bomb = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_manual_bomb.setGeometry(QtCore.QRect(1920, 800, 320, 40))
        self.pushButton_manual_bomb.setObjectName("pushButton_manual_bomb")
        # self.pushButton_16 = QtWidgets.QPushButton(self.centralwidget)
        # self.pushButton_16.setGeometry(QtCore.QRect(670, 560, 260, 30))
        # self.pushButton_16.setObjectName("pushButton_16")
        self.pushButton_refresh_data = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_refresh_data.setGeometry(QtCore.QRect(2240, 800, 320, 40))
        self.pushButton_refresh_data.setObjectName("pushButton_refresh_data")
        self.pushButton_auto_bomb_on = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_auto_bomb_on.setGeometry(QtCore.QRect(1920, 840, 320, 40))
        self.pushButton_auto_bomb_on.setObjectName("pushButton_auto_bomb_on")
        self.pushButton_auto_bomb_off = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_auto_bomb_off.setGeometry(QtCore.QRect(2240, 840, 320, 40))
        self.pushButton_auto_bomb_off.setObjectName("pushButton_auto_bomb_off")
        self.pushButton_control = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_control.setGeometry(QtCore.QRect(1920, 880, 320, 40))
        self.pushButton_control.setObjectName("pushButton_control")
        # self.pushButton_18 = QtWidgets.QPushButton(self.centralwidget)
        # self.pushButton_18.setGeometry(QtCore.QRect(350, 910, 260, 30))
        # self.pushButton_18.setObjectName("pushButton_18")
        # self.pushButton_19 = QtWidgets.QPushButton(self.centralwidget)
        # self.pushButton_19.setGeometry(QtCore.QRect(670, 910, 260, 30))
        # self.pushButton_19.setObjectName("pushButton_19")
        # self.pushButton_20 = QtWidgets.QPushButton(self.centralwidget)
        # self.pushButton_20.setGeometry(QtCore.QRect(1080, 860, 110, 30))
        # self.pushButton_20.setObjectName("pushButton_20")
        # self.pushButton_21 = QtWidgets.QPushButton(self.centralwidget)
        # self.pushButton_21.setGeometry(QtCore.QRect(350, 960, 260, 30))
        # self.pushButton_21.setObjectName("pushButton_21")
        # self.pushButton_22 = QtWidgets.QPushButton(self.centralwidget)
        # self.pushButton_22.setGeometry(QtCore.QRect(1690, 860, 110, 30))
        # self.pushButton_22.setObjectName("pushButton_22")
        # self.pushButton_23 = QtWidgets.QPushButton(self.centralwidget)
        # self.pushButton_23.setGeometry(QtCore.QRect(1310, 810, 260, 30))
        # self.pushButton_23.setObjectName("pushButton_23")
        # self.pushButton_24 = QtWidgets.QPushButton(self.centralwidget)
        # self.pushButton_24.setGeometry(QtCore.QRect(1310, 910, 260, 30))
        # self.pushButton_24.setObjectName("pushButton_24")
        # self.pushButton_25 = QtWidgets.QPushButton(self.centralwidget)
        # self.pushButton_25.setGeometry(QtCore.QRect(1310, 860, 260, 30))
        # self.pushButton_25.setObjectName("pushButton_25")
        # self.pushButton_26 = QtWidgets.QPushButton(self.centralwidget)
        # self.pushButton_26.setGeometry(QtCore.QRect(1575, 860, 110, 30))
        # self.pushButton_26.setObjectName("pushButton_26")
        # self.pushButton_27 = QtWidgets.QPushButton(self.centralwidget)
        # self.pushButton_27.setGeometry(QtCore.QRect(1805, 860, 110, 30))
        # self.pushButton_27.setObjectName("pushButton_27")
        # self.pushButton_28 = QtWidgets.QPushButton(self.centralwidget)
        # self.pushButton_28.setGeometry(QtCore.QRect(965, 860, 110, 30))
        # self.pushButton_28.setObjectName("pushButton_28")
        # self.pushButton_29 = QtWidgets.QPushButton(self.centralwidget)
        # self.pushButton_29.setGeometry(QtCore.QRect(1195, 860, 110, 30))
        # self.pushButton_29.setObjectName("pushButton_29")
        

        # self.label_1 = QtWidgets.QLabel(self.centralwidget)
        # self.label_1.setGeometry(QtCore.QRect(990, 560, 260, 30))
        # self.label_1.setObjectName("label_1")
        self.label_spd = QtWidgets.QLabel(self.centralwidget)
        self.label_spd.setGeometry(QtCore.QRect(320, 1100, 320, 50))
        self.label_spd.setObjectName("label_spd")
        # self.label_spd.setAlignment(QtCore.Qt.AlignTop)
        self.label_spd.setFont(font)
        
        self.label_battery = QtWidgets.QLabel(self.centralwidget)
        self.label_battery.setGeometry(QtCore.QRect(320, 1150, 320, 50))
        self.label_battery.setObjectName("label_battery")
        self.label_battery.setFont(font)
        # self.label_battery.setAlignment(QtCore.Qt.AlignTop)
        # self.label_4 = QtWidgets.QLabel(self.centralwidget)
        # self.label_4.setGeometry(QtCore.QRect(990, 610, 310, 30))
        # self.label_4.setObjectName("label_4")
        # self.label_5 = QtWidgets.QLabel(self.centralwidget)
        # self.label_5.setGeometry(QtCore.QRect(1310, 610, 310, 30))
        # self.label_5.setObjectName("label_5")
        # self.label_6 = QtWidgets.QLabel(self.centralwidget)
        # self.label_6.setGeometry(QtCore.QRect(1630, 610, 310, 30))
        # self.label_6.setObjectName("label_6")
        self.label_flight_mode = QtWidgets.QLabel(self.centralwidget)
        self.label_flight_mode.setGeometry(QtCore.QRect(1920, 1080, 640, 50))
        self.label_flight_mode.setObjectName("label_flight_mode")
        self.label_flight_mode.setFont(font)
        self.label_lat = QtWidgets.QLabel(self.centralwidget)
        self.label_lat.setGeometry(QtCore.QRect(640, 1100, 320, 50))
        self.label_lat.setObjectName("label_lat")
        self.label_lat.setFont(font)
        self.label_lon = QtWidgets.QLabel(self.centralwidget)
        self.label_lon.setGeometry(QtCore.QRect(640, 1150, 320, 50))
        self.label_lon.setObjectName("label_lon")
        self.label_lon.setFont(font)
        # self.label_10 = QtWidgets.QLabel(self.centralwidget)
        # self.label_10.setGeometry(QtCore.QRect(990, 710, 310, 30))
        # self.label_10.setObjectName("label_10")
        self.label_abs_alt = QtWidgets.QLabel(self.centralwidget)
        self.label_abs_alt.setGeometry(QtCore.QRect(0, 1150, 320, 50))
        self.label_abs_alt.setObjectName("label_abs_alt")
        self.label_abs_alt.setFont(font)
        self.label_rel_alt = QtWidgets.QLabel(self.centralwidget)
        self.label_rel_alt.setGeometry(QtCore.QRect(0, 1100, 320, 50))
        self.label_rel_alt.setObjectName("label_rel_alt")
        self.label_rel_alt.setFont(font)
        # self.label_13 = QtWidgets.QLabel(self.centralwidget)
        # self.label_13.setGeometry(QtCore.QRect(990, 760, 310, 30))
        # self.label_13.setObjectName("label_13")
        # self.label_14 = QtWidgets.QLabel(self.centralwidget)
        # self.label_14.setGeometry(QtCore.QRect(1310, 760, 310, 30))
        # self.label_14.setObjectName("label_14")
        # self.label_15 = QtWidgets.QLabel(self.centralwidget)
        # self.label_15.setGeometry(QtCore.QRect(1630, 760, 310, 30))
        # self.label_15.setObjectName("label_15")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1920, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        
        MainWindow.setWindowTitle(_translate("MainWindow", "NantongYufeng"))
        path = "file:\\" + os.getcwd() + "\\sources/save_map.html"
        path = path.replace('\\', '/')
        # self.qwebengine.load(QUrl(path))
        # self.pushButton.setText(_translate("MainWindow", "记录飞机所在位置为投弹点1"))
        # self.pushButton_2.setText(_translate("MainWindow", "记录飞机所在位置为投弹点2"))
        # self.pushButton_goto4.setText(_translate("MainWindow", "记录飞机所在位置为投弹点3"))
        self.pushButton_connect_plane.setText(_translate("MainWindow", "连接飞机"))
        self.pushButton_camera.setText(_translate("MainWindow", "连接视觉"))
        self.pushButton_scout_mission.setText(_translate("MainWindow", "执行侦察任务"))
        self.pushButton_goto1.setText(_translate("MainWindow", "前往投弹点1"))
        self.pushButton_goto2.setText(_translate("MainWindow", "前往投弹点2"))
        self.pushButton_goto3.setText(_translate("MainWindow", "前往投弹点3"))
        self.pushButton_goto4.setText(_translate("MainWindow", "前往投弹点4"))
        self.pushButton_arm.setText(_translate("MainWindow", "Arm"))
        self.pushButton_disarm.setText(_translate("MainWindow", "Disarm"))
        # self.pushButton_12.setText(_translate("MainWindow", "重启"))
        self.pushButton_kill.setText(_translate("MainWindow", "KILL"))
        # self.pushButton_14.setText(_translate("MainWindow", "自动投弹暂时有问题"))
        self.pushButton_manual_bomb.setText(_translate("MainWindow", "立即投弹(手动)"))
        # self.pushButton_16.setText(_translate("MainWindow", "启动目标追踪"))
        self.pushButton_refresh_data.setText(_translate("MainWindow", "开启数据追踪"))
        self.pushButton_auto_bomb_on.setText(_translate("MainWindow", "开启自动投弹"))
        self.pushButton_auto_bomb_off.setText(_translate("MainWindow", "关闭自动投弹"))
        self.pushButton_control.setText(_translate("MainWindow", "control"))
        # self.pushButton_18.setText(_translate("MainWindow", "相机向前"))
        # self.pushButton_19.setText(_translate("MainWindow", "相机向下"))
        # self.pushButton_20.setText(_translate("MainWindow", "左45"))
        # self.pushButton_21.setText(_translate("MainWindow", "刷新地图"))
        # self.pushButton_22.setText(_translate("MainWindow", "右45"))
        # self.pushButton_23.setText(_translate("MainWindow", "上升"))
        # self.pushButton_24.setText(_translate("MainWindow", "下降"))
        # self.pushButton_25.setText(_translate("MainWindow", "盘旋"))
        # self.pushButton_26.setText(_translate("MainWindow", "右15"))
        # self.pushButton_27.setText(_translate("MainWindow", "右90"))
        # self.pushButton_28.setText(_translate("MainWindow", "左90"))
        # self.pushButton_29.setText(_translate("MainWindow", "左15"))
        # self.pushButton_16.setDisabled(True)

        # self.label_1.setText(_translate("MainWindow", "高度:"+'下面写着呢'))
        self.label_spd.setText(_translate("MainWindow", "S:NULL"))
        self.label_battery.setText(_translate("MainWindow", "B:NULL"))
        # self.label_4.setText(_translate("MainWindow", "滚转角:"+roll_deg))
        # self.label_5.setText(_translate("MainWindow", "俯仰角:"+pitch_deg))
        # self.label_6.setText(_translate("MainWindow", "偏航角:"+yaw_deg))
        self.label_flight_mode.setText(_translate("MainWindow", "F_M:NULL"))
        self.label_lat.setText(_translate("MainWindow", "lat:NULL"))
        self.label_lon.setText(_translate("MainWindow", "lon:NULL"))
        # self.label_10.setText(_translate("MainWindow", "搜星数:"+num_sate))
        self.label_abs_alt.setText(_translate("MainWindow", "H(abs):NULL"))
        self.label_rel_alt.setText(_translate("MainWindow", "H(rel):NULL"))
        # self.label_13.setText(_translate("MainWindow", "滚转角速度:"+roll_speed))
        # self.label_14.setText(_translate("MainWindow", "俯仰角速度:"+pitch_speed))
        # self.label_15.setText(_translate("MainWindow", "偏航角速度:"+yaw_speed))

    def init_slots(self):
        self.pushButton_camera.clicked.connect(lambda: button_camera_open(self))
        self.timer_video.timeout.connect(lambda: show_video_frame(self))
        # self.pushButton_16.clicked.connect(self.open_camshift)
        self.pushButton_connect_plane.clicked.connect(lambda: connect_plane(self.drone, self.loop))
        # self.pushButton.clicked.connect(lambda: self.set_tar_pos(0))
        # self.pushButton_2.clicked.connect(lambda: self.set_tar_pos(1))
        
        self.pushButton_scout_mission.clicked.connect(lambda: scout_mission(self.drone, self.loop, self.waypoint_lists))
        self.pushButton_goto1.clicked.connect(lambda: goto(self.drone, self.loop, 0))
        self.pushButton_goto2.clicked.connect(lambda: goto(self.drone, self.loop, 1))
        self.pushButton_goto3.clicked.connect(lambda: goto(self.drone, self.loop, 2))
        self.pushButton_goto4.clicked.connect(lambda: goto(self.drone, self.loop, 3))
        self.pushButton_arm.clicked.connect(lambda: arm(self.drone, self.loop))
        self.pushButton_disarm.clicked.connect(lambda: disarm(self.drone, self.loop))
        # self.pushButton_12.clicked.connect(self.reboot)
        self.pushButton_kill.clicked.connect(lambda: kill_confirm(self.drone, self.loop, self))
        # self.pushButton_14.clicked.connect(self.bomb_mode)
        self.pushButton_manual_bomb.clicked.connect(lambda: drop_bomb(self.drone, self.loop))
        self.pushButton_refresh_data.clicked.connect(lambda: start_refresh(self.drone, self.loop, self))
        self.pushButton_auto_bomb_on.clicked.connect(lambda: auto_bomb_begin())
        self.pushButton_auto_bomb_off.clicked.connect(lambda: auto_bomb_end())
        # self.pushButton_control.clicked.connect(self.ControlFunction)
        # self.pushButton_18.clicked.connect(lambda: self.rudder_control(-0.6))
        # self.pushButton_19.clicked.connect(lambda: self.rudder_control(0))
        # self.pushButton_20.clicked.connect(lambda: self.go_deg(-45, 0))
        # self.pushButton_21.clicked.connect(lambda: self.debug_add_points())
        # self.pushButton_22.clicked.connect(lambda: self.go_deg(45, 0))
        # self.pushButton_23.clicked.connect(lambda: self.go_deg(0, 2))
        # self.pushButton_24.clicked.connect(lambda: self.go_deg(0, -2))
        # self.pushButton_25.clicked.connect(self.hold)
        # self.pushButton_26.clicked.connect(lambda: self.go_deg(15, 0))
        # self.pushButton_27.clicked.connect(lambda: self.go_deg(90, 0))
        # self.pushButton_28.clicked.connect(lambda: self.go_deg(-90, 0))
        # self.pushButton_29.clicked.connect(lambda: self.go_deg(-15, 0))
    
    def set_lim(self, x, y):
        # print("in set_lim")
        self.canvas.axes.set_xlim(x-0.003, x+0.003)
        self.canvas.axes.set_ylim(y-0.003, y+0.003)

    # def ControlFunction(self) :
    #     ControlWindow(self, self.loop, self.drone)