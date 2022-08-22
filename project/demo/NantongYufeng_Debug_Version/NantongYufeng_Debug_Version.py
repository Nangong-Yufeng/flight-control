# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\pythonWorkSpace\flight-control\project\demo\PyQt5\NantongYufeng\NantongYufeng.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from ast import arg
from concurrent.futures import thread
from glob import glob
from math import fabs
from operator import is_
from platform import release
import tarfile
from turtle import pos
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
import sys
import os
import folium
# import cv2
import argparse
import random
# import torch
import numpy as np
# import torch.backends.cudnn as cudnn
import threading
import asyncio
# from utils.torch_utils import select_device
# from models.experimental import attempt_load
# from utils.general import check_img_size, non_max_suppression, scale_coords, xyxy2xywh
# from utils.datasets import letterbox
# from utils.plots import plot_one_box
from mavsdk import System
from mavsdk.mission import *


hight = 'null'  # 高度
speed = 'null'  # 速度 1
battery = 'null'  # 电池
roll_deg = 'null'  # 滚转角
pitch_deg = 'null'  # 俯仰角
yaw_deg = 'null'  # 偏航角
flight_mode = 'null'  # 飞行模式
lat_deg = 'null'  # 纬度 1
lon_deg = 'null'  # 经度 1
num_sate = 'null'  # 搜到的卫星数
abs_alt = 'null'  # 绝对高度 1
rel_alt = 'null'  # 相对高度 1
roll_speed = 'null'  # 滚转角速度
pitch_speed = 'null'  # 俯仰角速度
yaw_speed = 'null'  # 偏航角速度
init_mavsdk_server = r'"sources\mavsdk-windows-x64-release\bin\mavsdk_server_bin.exe"' # 你要运行的exe文件

bomb_flag = False

pos_x = 320
pos_y = 240

tar_pos = [[22.5907503, 113.9623144], [22.58739, 113.96771],
       [22.58680, 113.96645]]  # 设置标靶坐标, 这个是为了goto和mission使用的
bomb_altitude = 30  # 设置投弹时的 **绝对** 高度
bomb_yaw = 0  # 设置投弹时的偏航角度 bomb
bomb_speed = 10  # 设置投弹时的速度

# drone = System(mavsdk_server_address='localhost', port=50051)
drone = System()

# =====Camshift Part=====
xs,ys,ws,hs = 0,0,0,0  #selection.x selection.y
xo,yo=0,0 #origin.x origin.y
selectObject = False
trackObject = 0
# term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )  # 设置迭代的终止标准，最多十次迭代
camshift_status = False
roi_hist = [[0.0]]
track_window=(0, 0, 0, 0)  # 设置跟踪框参数

# 调用高德地图http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}
Map = folium.Map(location=[22.5907, 113.9623],
                 zoom_start=16,
                 crs="EPSG3857", 
                 control_scale=True,
                 tiles='http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}',
                 attr='default')
folium.CircleMarker(
    location=[22.5907, 113.9623],
    radius=1,
    popup='popup',
    color='#DC143C',      # 圈的颜色
    fill=True,
    fill_color='#6495E'  # 填充颜色
).add_to(Map)
Map.add_child(folium.LatLngPopup())                     # 显示鼠标点击点经纬度
Map.add_child(folium.ClickForMarker(popup='Waypoint'))  # 将鼠标点击点添加到地图上
Map.save("save_map.html")

_translate = QtCore.QCoreApplication.translate
loop00 = asyncio.get_event_loop()
# 设置侦察任务
scout_mission = [MissionItem(tar_pos[0][0],
                             tar_pos[0][1],
                             25,
                             10,
                             True,
                             float('nan'),
                             float('nan'),
                             MissionItem.CameraAction.NONE,
                             float('nan'),
                             float('nan'),
                             float('nan'),
                             float('nan'),
                             float('nan')),
                 MissionItem(tar_pos[1][0],
                             tar_pos[1][1],
                             25,
                             10,
                             True,
                             float('nan'),
                             float('nan'),
                             MissionItem.CameraAction.NONE,
                             float('nan'),
                             float('nan'),
                             float('nan'),
                             float('nan'),
                             float('nan')),
                 MissionItem(tar_pos[2][0],
                             tar_pos[2][1],
                             25,
                             10,
                             True,
                             float('nan'),
                             float('nan'),
                             MissionItem.CameraAction.NONE,
                             float('nan'),
                             float('nan'),
                             float('nan'),
                             float('nan'),
                             float('nan'))]

class Ui_MainWindow(QMainWindow):
    def __init__(self, loop):
        super(QMainWindow, self).__init__()
        self.timer_video = QtCore.QTimer()
        self.loop = loop
        self.setupUi(self)
        self.init_cam()
        self.init_slots()
        # self.cap = cv2.VideoCapture()
        self.out = None

        parser = argparse.ArgumentParser()
        parser.add_argument('--weights', nargs='+', type=str,
                            default='weights/yolov5s.pt', help='model.pt path(s)')
        # file/folder, 0 for webcam
        parser.add_argument('--source', type=str,
                            default='data/images', help='source')
        parser.add_argument('--img-size', type=int,
                            default=640, help='inference size (pixels)')
        parser.add_argument('--conf-thres', type=float,
                            default=0.25, help='object confidence threshold')
        parser.add_argument('--iou-thres', type=float,
                            default=0.45, help='IOU threshold for NMS')
        parser.add_argument('--device', default='',
                            help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
        parser.add_argument(
            '--view-img', action='store_true', help='display results')
        parser.add_argument('--save-txt', action='store_true',
                            help='save results to *.txt')
        parser.add_argument('--save-conf', action='store_true',
                            help='save confidences in --save-txt labels')
        parser.add_argument('--nosave', action='store_true',
                            help='do not save images/videos')
        parser.add_argument('--classes', nargs='+', type=int,
                            help='filter by class: --class 0, or --class 0 2 3')
        parser.add_argument(
            '--agnostic-nms', action='store_true', help='class-agnostic NMS')
        parser.add_argument('--augment', action='store_true',
                            help='augmented inference')
        parser.add_argument('--update', action='store_true',
                            help='update all models')
        parser.add_argument('--project', default='runs/detect',
                            help='save results to project/name')
        parser.add_argument('--name', default='exp',
                            help='save results to project/name')
        parser.add_argument('--exist-ok', action='store_true',
                            help='existing project/name ok, do not increment')
        self.opt = parser.parse_args()
        print(self.opt)

        source, weights, view_img, save_txt, imgsz = self.opt.source, self.opt.weights, self.opt.view_img, self.opt.save_txt, self.opt.img_size

        # self.device = select_device(self.opt.device)
        # self.half = self.device.type != 'cpu'  # half precision only supported on CUDA

        # cudnn.benchmark = True

        # Load model
        # self.model = attempt_load(
        #     weights, map_location=self.device)  # load FP32 model
        # stride = int(self.model.stride.max())  # model stride
        # self.imgsz = check_img_size(imgsz, s=stride)  # check img_size
        # if self.half:
            # self.model.half()  # to FP16

        # Get names and colors
        # self.names = self.model.module.names if hasattr(
        #     self.model, 'module') else self.model.names
        # self.colors = [[random.randint(0, 255)
        #                 for _ in range(3)] for _ in self.names]


    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1080)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        # 新建一个QWebEngineView()对象
        self.qwebengine = QWebEngineView(self)
        # 设置网页在窗口中显示的位置和大小
        self.qwebengine.setGeometry(0, 0, 1200, 540)
        # 在QWebEngineView中加载网址
        # path = "file:\\/" + os.getcwd() + "\\project/NantongYufeng/sources/save_map.html"
        path = "file:\\/" + os.getcwd() + "\\save_map.html"
        
        path = path.replace('\\', '/')
        print('path=',path)
        self.qwebengine.load(QUrl(path))
        # self.centralwidget = QtWidgets.QWidget(MainWindow)
        # self.centralwidget.setObjectName("centralwidget")

        
        self.label_vision = QtWidgets.QLabel(self.centralwidget)
        self.label_vision.setGeometry(QtCore.QRect(1200, 0, 720, 540))
        self.label_vision.setObjectName("label_vision")

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(30, 610, 260, 30))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(350, 610, 260, 30))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(670, 610, 260, 30))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setGeometry(QtCore.QRect(30, 560, 260, 30))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_5 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_5.setGeometry(QtCore.QRect(350, 560, 260, 30))
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_6 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_6.setGeometry(QtCore.QRect(30, 660, 900, 30))
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_7 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_7.setGeometry(QtCore.QRect(30, 710, 260, 30))
        self.pushButton_7.setObjectName("pushButton_7")
        self.pushButton_8 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_8.setGeometry(QtCore.QRect(350, 710, 260, 30))
        self.pushButton_8.setObjectName("pushButton_8")
        self.pushButton_9 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_9.setGeometry(QtCore.QRect(670, 710, 260, 30))
        self.pushButton_9.setObjectName("pushButton_9")
        self.pushButton_10 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_10.setGeometry(QtCore.QRect(30, 810, 435, 30))
        self.pushButton_10.setObjectName("pushButton_10")
        self.pushButton_11 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_11.setGeometry(QtCore.QRect(495, 810, 435, 30))
        self.pushButton_11.setObjectName("pushButton_11")
        self.pushButton_12 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_12.setGeometry(QtCore.QRect(30, 860, 435, 30))
        self.pushButton_12.setObjectName("pushButton_12")
        self.pushButton_13 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_13.setGeometry(QtCore.QRect(495, 860, 435, 30))
        self.pushButton_13.setObjectName("pushButton_13")
        self.pushButton_14 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_14.setGeometry(QtCore.QRect(30, 760, 435, 30))
        self.pushButton_14.setObjectName("pushButton_14")
        self.pushButton_15 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_15.setGeometry(QtCore.QRect(495, 760, 435, 30))
        self.pushButton_15.setObjectName("pushButton_15")
        self.pushButton_16 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_16.setGeometry(QtCore.QRect(670, 560, 260, 30))
        self.pushButton_16.setObjectName("pushButton_16")
        self.pushButton_17 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_17.setGeometry(QtCore.QRect(30, 910, 260, 30))
        self.pushButton_17.setObjectName("pushButton_17")

        self.label_1 = QtWidgets.QLabel(self.centralwidget)
        self.label_1.setGeometry(QtCore.QRect(990, 560, 260, 30))
        self.label_1.setObjectName("label_1")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(1310, 560, 260, 30))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(1630, 560, 260, 30))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(990, 610, 310, 30))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(1310, 610, 310, 30))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(1630, 610, 310, 30))
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(990, 660, 310, 30))
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(1310, 660, 310, 30))
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(1630, 660, 310, 30))
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        self.label_10.setGeometry(QtCore.QRect(990, 710, 310, 30))
        self.label_10.setObjectName("label_10")
        self.label_11 = QtWidgets.QLabel(self.centralwidget)
        self.label_11.setGeometry(QtCore.QRect(1310, 710, 310, 30))
        self.label_11.setObjectName("label_11")
        self.label_12 = QtWidgets.QLabel(self.centralwidget)
        self.label_12.setGeometry(QtCore.QRect(1630, 710, 310, 30))
        self.label_12.setObjectName("label_12")
        self.label_13 = QtWidgets.QLabel(self.centralwidget)
        self.label_13.setGeometry(QtCore.QRect(990, 760, 310, 30))
        self.label_13.setObjectName("label_13")
        self.label_14 = QtWidgets.QLabel(self.centralwidget)
        self.label_14.setGeometry(QtCore.QRect(1310, 760, 310, 30))
        self.label_14.setObjectName("label_14")
        self.label_15 = QtWidgets.QLabel(self.centralwidget)
        self.label_15.setGeometry(QtCore.QRect(1630, 760, 310, 30))
        self.label_15.setObjectName("label_15")
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
        self.qwebengine.load(QUrl(path))
        self.pushButton.setText(_translate("MainWindow", "记录飞机所在位置为投弹点1"))
        self.pushButton_2.setText(_translate("MainWindow", "记录飞机所在位置为投弹点2"))
        self.pushButton_3.setText(_translate("MainWindow", "记录飞机所在位置为投弹点3"))
        self.pushButton_4.setText(_translate("MainWindow", "连接飞机"))
        self.pushButton_5.setText(_translate("MainWindow", "连接视觉"))
        self.pushButton_6.setText(_translate("MainWindow", "执行侦察任务"))
        self.pushButton_7.setText(_translate("MainWindow", "前往投弹点1"))
        self.pushButton_8.setText(_translate("MainWindow", "前往投弹点2"))
        self.pushButton_9.setText(_translate("MainWindow", "前往投弹点3"))
        self.pushButton_10.setText(_translate("MainWindow", "Arm"))
        self.pushButton_11.setText(_translate("MainWindow", "Disarm"))
        self.pushButton_12.setText(_translate("MainWindow", "重启"))
        self.pushButton_13.setText(_translate("MainWindow", "关机"))
        self.pushButton_14.setText(_translate("MainWindow", "自动投弹暂时有问题"))
        self.pushButton_15.setText(_translate("MainWindow", "立即投弹(手动)"))
        self.pushButton_16.setText(_translate("MainWindow", "启动目标追踪"))
        self.pushButton_17.setText(_translate("MainWindow", "开启数据追踪"))
        self.pushButton_16.setDisabled(True)

        self.label_1.setText(_translate("MainWindow", "高度:"+'下面写着呢'))
        self.label_2.setText(_translate("MainWindow", "速度:"+speed))
        self.label_3.setText(_translate("MainWindow", "电池:"+battery))
        self.label_4.setText(_translate("MainWindow", "滚转角:"+roll_deg))
        self.label_5.setText(_translate("MainWindow", "俯仰角:"+pitch_deg))
        self.label_6.setText(_translate("MainWindow", "偏航角:"+yaw_deg))
        self.label_7.setText(_translate("MainWindow", "飞行模式:"+flight_mode))
        self.label_8.setText(_translate("MainWindow", "纬度:"+lat_deg))
        self.label_9.setText(_translate("MainWindow", "经度:"+lon_deg))
        self.label_10.setText(_translate("MainWindow", "搜星数:"+num_sate))
        self.label_11.setText(_translate("MainWindow", "绝对高度:"+abs_alt))
        self.label_12.setText(_translate("MainWindow", "相对高度:"+rel_alt))
        self.label_13.setText(_translate("MainWindow", "滚转角速度:"+roll_speed))
        self.label_14.setText(_translate("MainWindow", "俯仰角速度:"+pitch_speed))
        self.label_15.setText(_translate("MainWindow", "偏航角速度:"+yaw_speed))

    def init_slots(self):
        self.pushButton_5.clicked.connect(self.button_camera_open)
        self.timer_video.timeout.connect(self.show_video_frame)
        self.pushButton_16.clicked.connect(self.open_camshift)
        self.pushButton_4.clicked.connect(self.connect_plane)
        self.pushButton.clicked.connect(lambda: self.set_tar_pos(0))
        self.pushButton_2.clicked.connect(lambda: self.set_tar_pos(1))
        self.pushButton_3.clicked.connect(lambda: self.set_tar_pos(2))
        self.pushButton_6.clicked.connect(self.scout_mission)
        self.pushButton_7.clicked.connect(lambda: self.goto(0))
        self.pushButton_8.clicked.connect(lambda: self.goto(1))
        self.pushButton_9.clicked.connect(lambda: self.goto(2))
        self.pushButton_10.clicked.connect(self.arm)
        self.pushButton_11.clicked.connect(self.disarm)
        self.pushButton_12.clicked.connect(self.reboot)
        self.pushButton_13.clicked.connect(self.kill)
        self.pushButton_14.clicked.connect(self.bomb_mode)
        self.pushButton_15.clicked.connect(self.drop_bomb)
        self.pushButton_17.clicked.connect(self.start_refresh)

# 数据更新模块
# 数据更新模块
# 数据更新模块

    async def refresh_position(self):
        global lat_deg, lon_deg, abs_alt, rel_alt
        async for position in drone.telemetry.position():
            # print(position)
            lat_deg = round(position.latitude_deg, 7)
            lon_deg = round(position.longitude_deg, 7)
            abs_alt = round(position.absolute_altitude_m, 2)
            rel_alt = round(position.relative_altitude_m, 2)
            self.label_8.setText(_translate("MainWindow", "纬度:"+str(lat_deg)))
            self.label_9.setText(_translate("MainWindow", "经度:"+str(lon_deg)))
            self.label_11.setText(_translate("MainWindow", "绝对高度:"+str(abs_alt)))
            self.label_12.setText(_translate("MainWindow", "相对高度:"+str(rel_alt)))

    async def refresh_airspd(self):
        global speed
        async for fixedwingmetrics in drone.telemetry.fixedwing_metrics():
            # print(fixedwingmetrics)
            speed = round(fixedwingmetrics.airspeed_m_s, 2)
            self.label_2.setText(_translate("MainWindow", "速度:"+str(speed)))

    async def refresh_battery(self):
        global battery
        async for drone_battery in drone.telemetry.battery():
            battery = round(drone_battery.remaining_percent, 2)
            self.label_3.setText(_translate("MainWindow", "电池"+str(battery)))

    async def refresh_angularvelocity(self):
        global roll_speed, pitch_speed, yaw_speed
        async for AngularVelocity in drone.telemetry.attitude_angular_velocity_body():
            roll_speed = round(AngularVelocity.roll_rad_s, 2)
            pitch_speed = round(AngularVelocity.pitch_rad_s, 2)
            yaw_speed = round(AngularVelocity.yaw_rad_s, 2)
            self.label_13.setText(_translate("MainWindow", "滚转角速度:"+str(roll_speed)))
            self.label_14.setText(_translate("MainWindow", "俯仰角速度:"+str(pitch_speed)))
            self.label_15.setText(_translate("MainWindow", "偏航角速度:"+str(yaw_speed)))

    async def refresh_eulerangle(self):
        global roll_deg, pitch_deg, yaw_deg
        async for eularangle in drone.telemetry.attitude_euler():
            roll_deg = round(eularangle.roll_deg, 2)
            pitch_deg = round(eularangle.pitch_deg, 2)
            yaw_deg = round(eularangle.yaw_deg, 2)
            self.label_4.setText(_translate("MainWindow", "滚转角:"+str(roll_deg)))
            self.label_5.setText(_translate("MainWindow", "俯仰角:"+str(pitch_deg)))
            self.label_6.setText(_translate("MainWindow", "偏航角:"+str(yaw_deg)))

    async def refresh_flightmode(self):
        global flight_mode
        async for FM in drone.telemetry.flight_mode():
            flight_mode = FM
            self.label_7.setText(_translate("MainWindow", "飞行模式:"+str(flight_mode)))

    async def refresh_num_satellites(self):
        global num_sate
        async for gpsinfo in drone.telemetry.gps_info():
            num_sate = gpsinfo.num_satellites
            self.label_10.setText(_translate("MainWindow", "搜星数:"+str(num_sate)))

    def set_tar_pos(self, i):
        global tar_pos
        set_tar_pos_thread = threading.Thread(target=self.set_tar_pos_thread, args=(i, tar_pos))
        set_tar_pos_thread.start()

    def set_tar_pos_thread(self, i, tar_pos):
        # loop = asyncio.new_event_loop()
        # tasks = [self.set_tar_pos_drone(i, tar_pos)]
        self.loop.run_until_complete(self.set_tar_pos_drone(i, tar_pos))
        # loop.close

    async def set_tar_pos_drone(self, i, tar_pos):
        global drone
        async for position in drone.telemetry.position():
            tar_pos[i] = [position.latitude_deg, position.longitude_deg]
            print('tar_pos[', i, ']', '=', tar_pos[i])
            return position

    def connect_plane(self):
        # mavsdk_thread = threading.Thread(target=self.open_mavsdk_server)
        # mavsdk_thread.start()
        connect_plane_thread = threading.Thread(target=self.connect_plane_thread)
        connect_plane_thread.start()

    def open_mavsdk_server(self):
        server = os.system(init_mavsdk_server)
        print (server)

    def connect_plane_thread(self):
        global drone
        # loop = asyncio.new_event_loop()
        # tasks = [self.drone_connect(drone)]
        # loop.run_until_complete(asyncio.wait(tasks))
        # loop.close
        self.loop.run_until_complete(self.drone_connect(drone))

    async def drone_connect(self, drone):
        # print('before connect')
        await drone.connect(system_address="udp://:14540")
        print('connect success')
        

    def start_refresh(self):
        threading.Thread(target=self.start_refresh_thread).start()

    def start_refresh_thread(self):
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        tasks = [self.refresh_airspd(), self.refresh_position(), self.refresh_angularvelocity(), self.refresh_battery(), self.refresh_eulerangle(), self.refresh_flightmode(), self.refresh_num_satellites()]
        self.loop.run_until_complete(asyncio.wait(tasks))
        # loop.close

    def scout_mission(self):
        scout_mission_thread = threading.Thread(target=self.scout_mission_thread)
        scout_mission_thread.start()

    def scout_mission_thread(self):
        # loop = asyncio.new_event_loop()
        # tasks = [self.scout_mission_drone(scout_mission, False)]
        self.loop.run_until_complete(self.scout_mission_drone(scout_mission, False))
        # loop.close

    async def scout_mission_drone(self, mission_items, is_back):
        global drone
        # termination_task = asyncio.ensure_future(
        #     self.observe_is_in_air(drone))

        mission_plan = MissionPlan(mission_items)

        await drone.mission.set_return_to_launch_after_mission(is_back)

        print("-- Uploading mission")
        await drone.mission.upload_mission(mission_plan)

        print("-- Starting mission")
        await drone.mission.start_mission()

        # await termination_task

    async def observe_is_in_air(self, drone):
        """ Monitors whether the drone is flying or not and
        returns after landing """

        was_in_air = False
        was_mission_finished = False
        is_mission_finished = False

        async for mission_progress in drone.mission.mission_progress():
            print(f"Mission progress: "
                f"{mission_progress.current}/"
                f"{mission_progress.total}")

            if mission_progress.current == mission_progress.total:
                print("is_mission_finished = True")
                is_mission_finished = True

            if not was_mission_finished and is_mission_finished:
                await asyncio.get_event_loop().shutdown_asyncgens()
                return

    def goto(self, i):
        goto_thread = threading.Thread(target=self.goto_thread, args=(i, ))
        goto_thread.start()

    def goto_thread(self, i):
        # loop = asyncio.new_event_loop()
        # tasks = [self.goto_drone(tar_pos[i], bomb_altitude, bomb_yaw, bomb_speed)]
        self.loop.run_until_complete(self.goto_drone(tar_pos[i], bomb_altitude, bomb_yaw, bomb_speed))
        # loop.close

    async def goto_drone(self, target, altitude, yaw, speed):
        global drone
        # if not await drone.mission.is_mission_finished():
        #     await drone.mission.pause_mission()
        print("Going to", end=" ")
        print(target)
        await drone.action.goto_location(target[0], target[1], altitude, yaw)  # 前往投弹坐标, 高度, 偏航角
        await drone.action.set_current_speed(speed)  # 设置速度

    def arm(self):
        arm_thread = threading.Thread(target=self.arm_thread)
        arm_thread.start()

    def arm_thread(self):
        # loop = asyncio.new_event_loop()
        # tasks = [self.arm_drone()]
        self.loop.run_until_complete(self.arm_drone())
        # loop.close

    async def arm_drone(self):
        global drone
        await drone.action.arm()

    def disarm(self):
        disarm_thread = threading.Thread(target=self.disarm_thread)
        disarm_thread.start()

    def disarm_thread(self):
        # loop = asyncio.new_event_loop()
        # tasks = [self.disarm_drone()]
        self.loop.run_until_complete(self.disarm_drone())
        # loop.close

    async def disarm_drone(self):
        global drone
        await drone.action.disarm()

    def reboot(self):
        reboot_thread = threading.Thread(target=self.reboot_thread)
        reboot_thread.start()

    def reboot_thread(self):
        # loop = asyncio.new_event_loop()
        # tasks = [self.reboot_drone()]
        self.loop.run_until_complete(self.reboot_drone())
        # loop.close

    async def reboot_drone(self):
        global drone
        await drone.action.reboot()

    def kill(self):
        kill_thread = threading.Thread(target=self.kill_thread)
        kill_thread.start()

    def kill_thread(self):
        # loop = asyncio.new_event_loop()
        tasks = [self.kill_drone()]
        self.loop.run_until_complete(self.kill_drone())
        # loop.close

    async def kill_drone(self):
        global drone
        await drone.action.kill()

    def bomb_mode(self):
        bomb_mode_thread = threading.Thread(target=self.bomb_mode_thread)
        bomb_mode_thread.start()

    def bomb_mode_thread(self):
        # loop = asyncio.new_event_loop()
        # tasks = [self.bomb_mode_drone()]
        self.loop.run_until_complete(self.bomb_mode_drone())
        # loop.close

    async def bomb_mode_drone(self):
        global drone
        while(True):
            if(bomb_flag):
                await self.drop_bomb_drone()
                break

    def drop_bomb(self):
        drop_bomb_thread = threading.Thread(target=self.drop_bomb_thread)
        drop_bomb_thread.start()

    def drop_bomb_thread(self):
        # loop = asyncio.new_event_loop()
        # tasks = [self.drop_bomb_drone()]
        self.loop.run_until_complete(self.drop_bomb_drone())
        # loop.close

    async def drop_bomb_drone(self):
        global drone
        await drone.action.set_actuator(1, -0.9)
        await asyncio.sleep(2)
        await drone.action.set_actuator(1, 0.9)

    def open_camshift(self):
        global camshift_status
        # cv2.namedWindow('RANX_AI')
        # cv2.setMouseCallback('RANX_AI',self.onMouse)
        
        camshift_status = True

    def init_cam(self):
        global camshift_status, xs, ys, ws, hs, xo, yo, selectObject, trackObject
        pix = QtGui.QPixmap('sources/no_camera.png')
        self.label_vision.setPixmap(pix)
        camshift_status = False
        xs,ys,ws,hs = 0,0,0,0  #selection.x selection.y
        xo,yo=0,0 #origin.x origin.y
        selectObject = False
        trackObject = 0

    def button_camera_open(self):
        if not self.timer_video.isActive():
            # 默认使用第一个本地camera
            flag = self.cap.open(0)
            if flag == False:
                QtWidgets.QMessageBox.warning(
                    self, u"Warning", u"打开摄像头失败", buttons=QtWidgets.QMessageBox.Ok, defaultButton=QtWidgets.QMessageBox.Ok)
            else:
                # self.out = cv2.VideoWriter('prediction.avi', cv2.VideoWriter_fourcc(
                #     *'MJPG'), 20, (int(self.cap.get(3)), int(self.cap.get(4))))
                # self.timer_video.start(30)
                self.pushButton_5.setText(u"关闭视觉")
                self.pushButton_16.setDisabled(False)
        else:
            self.timer_video.stop()
            self.cap.release()
            self.out.release()
            self.label_vision.clear()
            self.init_cam()
            self.pushButton_5.setText(u"连接视觉")
            self.pushButton_16.setDisabled(True)

    def show_video_frame(self):
        global trackObject, roi_hist, track_window
        name_list = []
        img_list = []

        flag, img = self.cap.read()
        if img is not None:
            showimg = img
        #     with torch.no_grad():
        #         img = letterbox(img, new_shape=self.opt.img_size)[0]
        #         # Convert
        #         # BGR to RGB, to 3x416x416
        #         img = img[:, :, ::-1].transpose(2, 0, 1)
        #         img = np.ascontiguousarray(img)
        #         img = torch.from_numpy(img).to(self.device)
        #         img = img.half() if self.half else img.float()  # uint8 to fp16/32
        #         img /= 255.0  # 0 - 255 to 0.0 - 1.0
        #         if img.ndimension() == 3:
        #             img = img.unsqueeze(0)
        #         # Inference
        #         pred = self.model(img, augment=self.opt.augment)[0]

        #         # Apply NMS
        #         pred = non_max_suppression(pred, self.opt.conf_thres, self.opt.iou_thres, classes=self.opt.classes,
        #                                    agnostic=self.opt.agnostic_nms)
        #         # Process detections
        #         for i, det in enumerate(pred):  # detections per image
        #             if det is not None and len(det):
        #                 # Rescale boxes from img_size to im0 size
        #                 det[:, :4] = scale_coords(
        #                     img.shape[2:], det[:, :4], showimg.shape).round()
        #                 # Write results
        #                 for *xyxy, conf, cls in reversed(det):
        #                     xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) ).view(-1).tolist()
        #                     label = '%s %.2f' % (self.names[int(cls)], conf)
        #                     # label = '%s' % (self.names[int(cls)])
        #                     img_list.append(xywh)
        #                     name_list.append(self.names[int(cls)])
        #                     print(label)
        #                     plot_one_box(
        #                         xyxy, showimg, label=label, color=self.colors[int(cls)], line_thickness=2)

        #                 bombthread_yolo = threading.Thread(target=self.bomb_func)
        #                 if ((len(img_list) > 0) & ('red' in name_list)):  # 如果检测到目标
        #                     # print(cls_object[0],img_object[0][0], img_object[0][1], img_object[0][2], img_object[0][3])bomb
        #                     for i in range(len(img_list)):
        #                         distx = fabs(img_list[i][0]-pos_x)
        #                         disty = fabs(img_list[i][1]-pos_y)
        #                         if (distx**2 + disty**2) <= 625:  # 如果目标在以中心为圆心，25像素为半径的圆
        #                             # count = i
        #                             flag = True
        #                             print("Bomb YoloV5", end=': ')
        #                             print(name_list[i],img_list[i][0], img_list[i][1], img_list[i][2], img_list[i][3])
        #                             bombthread_yolo.start()
        #                             bombthread_yolo.join()
        #                             break
                    
        #             cv2.circle(showimg, (pos_x, pos_y), 25, (255, 0, 0), 2)

        #             if trackObject != 0:
        #                 hsv =  cv2.cvtColor(showimg, cv2.COLOR_BGR2HSV)  # RGB转为HSV更好处理
        #                 mask = cv2.inRange(hsv, np.array((0., 30.,10.)), np.array((180.,256.,255.)))
        #                 if trackObject == -1:
        #                     track_window=(xs,ys,ws,hs)  # 设置跟踪框参数
        #                     maskroi = mask[ys:ys+hs, xs:xs+ws]
        #                     hsv_roi = hsv[ys:ys+hs, xs:xs+ws]
        #                     roi_hist = cv2.calcHist([hsv_roi],[0],maskroi,[180],[0,180])

        #                     cv2.normalize(roi_hist,roi_hist,0,255,cv2.NORM_MINMAX)
        #                     trackObject = 1
        #                 dst = cv2.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)
        #                 dst &= mask
        #                 ret, track_window = cv2.CamShift(dst, track_window, term_crit)
        #                 pts = cv2.boxPoints(ret)
        #                 pts = np.int0(pts)
        #                 # print("pts = ", pts)
        #                 target_x = (pts[0][0]+pts[1][0]+pts[2][0]+pts[3][0]) / 4
        #                 target_y = (pts[0][1]+pts[1][1]+pts[2][1]+pts[3][1]) / 4
        #                 distx_cs = fabs(target_x-pos_x)
        #                 disty_cs = fabs(target_y-pos_y)
        #                 if (distx_cs**2 + disty_cs**2) <= 625:  # 如果目标在以中心为圆心，25像素为半径的圆
        #                     bombthread_cs = threading.Thread(target=self.bomb_func)
        #                     print("Bomb CamShift", end=': ')
        #                     print(target_x, target_y)
        #                     bombthread_cs.start()
        #                     bombthread_cs.join()
        #                 img2 = cv2.polylines(showimg,[pts],True, 255,2)
        #             if(camshift_status): 
        #                 cv2.imshow('RANX_AI', showimg)
        #     self.out.write(showimg)
        #     show = cv2.resize(showimg, (720, 540))
        #     self.result = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)
        #     showImage = QtGui.QImage(self.result.data, self.result.shape[1], self.result.shape[0],
        #                              QtGui.QImage.Format_RGB888)
        #     self.label_vision.setPixmap(QtGui.QPixmap.fromImage(showImage))

        else:
            self.timer_video.stop()
            self.cap.release()
            self.out.release()
            self.label_vision.clear()
            self.pushButton_5.setDisabled(False)
            self.init_cam()

    def bomb_func(self):
        global bomb_flag
        print('===========BOMB_FUNC===========')
        bomb_flag = True
        # aString = 'bomb'
        # wc.OpenClipboard()
        # wc.EmptyClipboard()
        # wc.SetClipboardData(win32con.CF_TEXT, aString.encode('GBK')) # 解决中文乱码
        # wc.CloseClipboard()

    def onMouse(self, event, x, y, flags, prams):  # 设置跟踪框参数
        global xs,ys,ws,hs,selectObject,xo,yo,trackObject
        # if selectObject == True:
        #     xs = min(x, xo)
        #     ys = min(y, yo)
        #     ws = abs(x-xo)
        #     hs = abs(y-yo)
        # if event == cv2.EVENT_LBUTTONDOWN:
        #     xo,yo = x, y
        #     xs,ys,ws,hs= x, y, 0, 0
        #     selectObject = True
        # elif event == cv2.EVENT_LBUTTONUP:
        #     selectObject = False
        #     trackObject = -1


if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = asyncio.get_event_loop()
    my_MainWindow = Ui_MainWindow(loop)
    # my_MainWindow.setupUi(my_MainWindow)
    my_MainWindow.show()
    sys.exit(app.exec_())