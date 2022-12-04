import cv2
import threading
import asyncio
import nest_asyncio
import numpy as np
import matplotlib
import math
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg # pyqt5的画布
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from mavsdk import System
from PIL import ImageDraw
from utils.DroneUtils import kill_thread, drop_bomb_thread
from utils.NGYFDetector.NGYFDetector import NGYFDetector

global_lat = []
global_lon = []
x_data = []
y_data = []
auto_bomb_flag = False
detect_flag = True # True为未侦察结束, False为侦察结束
bomb_gps = [0, 0]

nest_asyncio.apply()
_translate = QtCore.QCoreApplication.translate

detector = NGYFDetector()
b_blk = np.zeros((1920, 1080), np.uint8)
cv2.rectangle(b_blk, (480, 0), (1440, 100), (255, 0, 0), -1)
r_blk = np.zeros((1920, 1080), np.uint8)
cv2.rectangle(r_blk, (480, 0), (1440, 100), (0, 0, 255), -1)
font = cv2.FONT_HERSHEY_SIMPLEX


class MyMatPlotAnimation(FigureCanvasQTAgg):
    """
    创建一个画板类，并把画布放到容器（画板上）FigureCanvasQTAgg，再创建一个画图区
    """
    def __init__(self, width=10, heigh=10, dpi=100):
        # 创建一个Figure,该Figure为matplotlib下的Figure，不是matplotlib.pyplot下面的Figure
        self.figs = Figure(figsize=(width, heigh), dpi=dpi)
        super(MyMatPlotAnimation, self).__init__(self.figs)
        self.figs.patch.set_facecolor('#01386a') # 设置绘图区域颜色
        self.axes = self.figs.add_subplot(111)
        self.axes.set_xlim(47.397, 47.398)
        self.axes.set_ylim(8.545, 8.546)
        
    
    def set_mat_func(self, t, s):
        """
        初始化设置函数
        """
        self.t = t
        self.s = s
        # self.axes.cla()
        self.axes.patch.set_facecolor("#01386a") # 设置ax区域背景颜色
        self.axes.patch.set_alpha(0.5) # 设置ax区域背景颜色透明度
        # self.axes.spines['top'].set_color('#01386a')
        self.axes.spines['top'].set_visible(False) # 顶边界不可见
        self.axes.spines['right'].set_visible(False) # 右边界不可见
        self.axes.xaxis.set_ticks_position('bottom') # 设置ticks（刻度）的位置为下方
        self.axes.yaxis.set_ticks_position('left') # 设置ticks（刻度） 的位置为左侧
        # 设置左、下边界在（0，0）处相交
        # self.axes.spines['bottom'].set_position(('data', 0)) # 设置x轴线再Y轴0位置
        self.axes.spines['left'].set_position(('data', 0)) # 设置y轴在x轴0位置
        self.plot_line, = self.axes.plot([], [], 'r-', linewidth=1) # 注意‘,'不可省略

    def plot_tick(self):
        plot_line = self.plot_line
        plot_axes = self.axes
        t = self.t
        def upgrade(frames): # 注意这里是plot_tick方法内的嵌套函数
            global x_data, y_data
            # print(frames)
            # for i in range(len(t)):
            # x_data.append(frames)
            # y_data.append(frames)
            # print(x_data)
            plot_axes.plot(global_lat, global_lon, 'r-', linewidth=1)
            self.figs.canvas.draw() # 重绘还是必须要的
            return plot_line, # 这里也是注意‘,'不可省略，否则会报错
        ani = FuncAnimation(self.figs, upgrade, frames=np.linspace(0, 4, 12800), blit=True, repeat=False)
        self.figs.canvas.draw() # 重绘还是必须要的
        

def plotcos(MainWindow):
    t = np.arange(0.0, 5.0, 0.01)
    s = np.cos(2 * np.pi * t)
    MainWindow.canvas.set_mat_func(t, s)
    MainWindow.canvas.plot_tick()

def init_cam(MainWindow):
    # pix = QtGui.QPixmap('sources/img/no_camera.png')
    img = QtGui.QImage("sources/img/no_camera.png")
    size = QSize(1920, 1080)
    pixImg = QtGui.QPixmap.fromImage(img.scaled(size, Qt.IgnoreAspectRatio))
    MainWindow.label_vision.setPixmap(pixImg)

def kill_confirm(drone, loop, MainWindow):
    reply = QMessageBox.question(MainWindow, 'kill?', '您想要自杀吗?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    if(reply == QMessageBox.Yes):
        killthread = threading.Thread(target=kill_thread, args=(drone, loop))
        killthread.start()

def button_camera_open(MainWindow):
    if not MainWindow.timer_video.isActive():
        # 默认使用第一个本地camera
        flag = MainWindow.cap.open(0)
        if flag == False:
            QtWidgets.QMessageBox.warning(
                MainWindow, u"Warning", u"打开摄像头失败", buttons=QtWidgets.QMessageBox.Ok, defaultButton=QtWidgets.QMessageBox.Ok)
        else:
            MainWindow.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))
            MainWindow.cap.set(cv2.CAP_PROP_FPS, 30)
            MainWindow.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            MainWindow.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            MainWindow.out = cv2.VideoWriter('prediction.avi', cv2.VideoWriter_fourcc(
                *'MJPG'), 30, (int(MainWindow.cap.get(3)), int(MainWindow.cap.get(4))))
            MainWindow.timer_video.start(30)
            MainWindow.pushButton_camera.setText(u"关闭视觉")
            # MainWindow.pushButton_16.setDisabled(False)
    else:
        MainWindow.timer_video.stop()
        MainWindow.cap.release()
        MainWindow.out.release()
        MainWindow.label_vision.clear()
        init_cam(MainWindow)
        MainWindow.pushButton_camera.setText(u"连接视觉")
        # MainWindow.pushButton_16.setDisabled(True)

def mid_num(array):
    array.sort()
    return array[1] # 返回中位数

def select_num(array, targets, nums):
    ret = [[], []]
    for i in range(len(array[0])):
        if array[0][i] in nums:
            ret[0].append(array[0][i])
            ret[1].append(array[1][i])
            add_target_num(targets, array[0][i])
    return ret

def add_target_num(array, num):
    global detect_flag

    if num not in array:
        array.append(num)
        print("识别结果: {}".format(num))
        if len(array) == 3:
            detect_flag = False
            print("识别结束, 结果为: {}中位数为:{}".format(array, mid_num(array)))

def show_video_frame(MainWindow):
    global auto_bomb_flag

    # detector = NGYFDetector()
    flag, img = MainWindow.cap.read()
    
    if flag: 
        if detect_flag: 
            res = detector.detect(img)
            res = select_num(res, MainWindow.targets, [3, 47, 90]) # 
            if(auto_bomb_flag):
                # for i in range(len(res[0])):
                #     point = (res[1][i][0][0], res[1][i][0][1])
                #     if(point[0])
                
                for i in range(len(res[0])):
                    cv2.ellipse(img, tuple(map(int, res[1][i][0])), tuple(map(int, res[1][i][1])), res[1][i][2], 0, 360, (114, 255, 191), 2);
                    point = (res[1][i][0][0]+res[1][i][1][1]*math.cos(math.radians(res[1][i][2])), res[1][i][0][1]+res[1][i][1][1]*math.sin(math.radians(res[1][i][2])))
                    cv2.putText(img, str(res[0][i]), tuple(map(int, point)), font, 1, (0, 0, 255), 2)
                    point = (res[1][i][0][0], res[1][i][0][1])
                    if(480 < point[0] < 1440) and (0 < point[1] < 100):
                        threading.Thread(target=drop_bomb_thread, args=(MainWindow.drone, MainWindow.loop)).start()
                        print("===BOMB===BOMB===BOMB===BOMB===")
                        auto_bomb_flag = False
                        break
                if(auto_bomb_flag):
                    img = cv2.addWeighted(img, 1.0, b_blk, 0.5, 1)
                else:
                    img = cv2.addWeighted(img, 1.0, r_blk, 0.5, 1)
            else:
                
                for i in range(len(res[0])):
                    cv2.ellipse(img, tuple(map(int, res[1][i][0])), tuple(map(int, res[1][i][1])), res[1][i][2], 0, 360, (114, 255, 191), 2);
                    point = (res[1][i][0][0]+res[1][i][1][1]*math.cos(math.radians(res[1][i][2])), res[1][i][0][1]+res[1][i][1][1]*math.sin(math.radians(res[1][i][2])))
                    cv2.putText(img, str(res[0][i]), tuple(map(int, point)), font, 1, (0, 0, 255), 2)
        MainWindow.out.write(img)
        show = cv2.resize(img, (1920, 1080))
        MainWindow.result = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)
        showImage = QtGui.QImage(MainWindow.result.data, MainWindow.result.shape[1], MainWindow.result.shape[0],
                                    QtGui.QImage.Format_RGB888)
        MainWindow.label_vision.setPixmap(QtGui.QPixmap.fromImage(showImage))

    else:
        MainWindow.timer_video.stop()
        MainWindow.cap.release()
        MainWindow.out.release()
        MainWindow.label_vision.clear()
        MainWindow.pushButton_camera.setDisabled(False)
        init_cam(MainWindow)

async def set_map(drone: System, MainWindow):
    async for position in drone.telemetry.position():
        lat_deg = round(position.latitude_deg, 7)
        lon_deg = round(position.longitude_deg, 7)
        # MainWindow.canvas.axes.set_xlim(lat_deg-0.0015, lat_deg+0.0015)
        # MainWindow.canvas.axes.set_ylim(lon_deg-0.0015, lon_deg+0.0015)
        MainWindow.set_lim(lat_deg, lon_deg)
        break; # do nothing

async def refresh_position(drone:System, MainWindow):
    i = 0
    global global_lat, global_lon
    async for position in drone.telemetry.position():
        i += 1
        
        lat_deg = round(position.latitude_deg, 7)
        lon_deg = round(position.longitude_deg, 7)
        
        abs_alt = round(position.absolute_altitude_m, 2)
        rel_alt = round(position.relative_altitude_m, 2)
        
        MainWindow.label_lat.setText(_translate("MainWindow", "lat:"+str(lat_deg)))
        MainWindow.label_lon.setText(_translate("MainWindow", "lon:"+str(lon_deg)))
        MainWindow.label_abs_alt.setText(_translate("MainWindow", "H(abs):"+str(abs_alt)))
        MainWindow.label_rel_alt.setText(_translate("MainWindow", "H(rel):"+str(rel_alt)))
        if(i % 3 == 0):
            # print("------add figure------")
            global_lat.append(lat_deg)
            global_lon.append(lon_deg)
            # print(lat_deg, lon_deg)

async def refresh_airspd(drone:System, MainWindow):
    # async for timestamp_us, latitude_deg, longitude_deg, absolute_altitude_m, hdop, vdop, velocity_m_s, cog_deg, altitude_ellipsoid_m, horizontal_uncertainty_m, vertical_uncertainty_m, velocity_uncertainty_m_s, heading_uncertainty_deg, yaw_deg in drone.telemetry.RawGps():
        # print(fixedwingmetrics)
        # print("velocity_m_s = {}".format(velocity_m_s))
        # print("velocity_uncertainty_m_s = {}".format(velocity_uncertainty_m_s))
    # print("in refresh airspd")
    async for velocity in drone.telemetry.velocity_ned():
        # print("north_m_s = {}".format(velocity.north_m_s))
        # print("east_m_s = {}".format(velocity.east_m_s))
        speed = math.sqrt(velocity.north_m_s*velocity.north_m_s + velocity.east_m_s*velocity.east_m_s)
        speed = round(speed, 2)
        MainWindow.label_spd.setText(_translate("MainWindow", "S:"+str(speed)))

async def refresh_battery(drone:System, MainWindow):
    async for drone_battery in drone.telemetry.battery():
        battery = round(drone_battery.remaining_percent, 2)
        battery = 2.2 * battery + 2.0
        MainWindow.label_battery.setText(_translate("MainWindow", "B:"+str(battery)))

async def refresh_flightmode(drone:System, MainWindow):
    async for FM in drone.telemetry.flight_mode():
        flight_mode = FM
        MainWindow.label_flight_mode.setText(_translate("MainWindow", "F_M:"+str(flight_mode)))

def start_refresh(drone, loop, MainWindow):
    threading.Thread(target=start_refresh_thread, args=(drone, loop, MainWindow)).start()

def start_refresh_thread(drone:System, loop, MainWindow):
    loop.run_until_complete(set_map(drone, MainWindow))
    tasks = [refresh_airspd(drone, MainWindow), refresh_position(drone, MainWindow), refresh_battery(drone, MainWindow), refresh_flightmode(drone, MainWindow)]
    loop.run_until_complete(asyncio.wait(tasks))

def auto_bomb_begin():
    global auto_bomb_flag
    auto_bomb_flag = True

def auto_bomb_end():
    global auto_bomb_flag
    auto_bomb_flag = False