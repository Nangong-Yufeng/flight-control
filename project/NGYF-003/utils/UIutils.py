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

nest_asyncio.apply()
_translate = QtCore.QCoreApplication.translate

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
        flag = MainWindow.cap.open("utils/NGYFDetector/WIN_20221026_16_51_17_Pro.mp4")
        if flag == False:
            QtWidgets.QMessageBox.warning(
                MainWindow, u"Warning", u"打开摄像头失败", buttons=QtWidgets.QMessageBox.Ok, defaultButton=QtWidgets.QMessageBox.Ok)
        else:
            MainWindow.out = cv2.VideoWriter('prediction.avi', cv2.VideoWriter_fourcc(
                *'MJPG'), 20, (int(MainWindow.cap.get(3)), int(MainWindow.cap.get(4))))
            MainWindow.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))
            MainWindow.cap.set(cv2.CAP_PROP_FPS, 30)
            MainWindow.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            MainWindow.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
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

def show_video_frame(MainWindow):
    global auto_bomb_flag

    detector = NGYFDetector()
    flag, img = MainWindow.cap.read()
    b_blk = np.zeros(img.shape, np.uint8)
    cv2.rectangle(b_blk, (640, 0), (1280, 100), (255, 0, 0), -1)
    r_blk = np.zeros(img.shape, np.uint8)
    cv2.rectangle(b_blk, (640, 0), (1280, 100), (0, 0, 255), -1)
    font = cv2.FONT_HERSHEY_SIMPLEX
    if flag: 
        res = detector.detect(img)
        if(auto_bomb_flag):
            # for i in range(len(res[0])):
            #     point = (res[1][i][0][0], res[1][i][0][1])
            #     if(point[0])
            
            
            
            for i in range(len(res[0])):
                cv2.ellipse(img, tuple(map(int, res[1][i][0])), tuple(map(int, res[1][i][1])), res[1][i][2], 0, 360, (114, 255, 191), 2);
                point = (res[1][i][0][0]+res[1][i][1][1]*math.cos(math.radians(res[1][i][2])), res[1][i][0][1]+res[1][i][1][1]*math.sin(math.radians(res[1][i][2])))
                cv2.putText(img, str(res[0][i]), tuple(map(int, point)), font, 1, (0, 0, 255), 2)
                point = (res[1][i][0][0], res[1][i][0][1])
                if(640 < point[0] < 1280) and (0 < point[1] < 100):
                    threading.Thread(target=drop_bomb_thread, args=(MainWindow.drone, MainWindow.loop))
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
        MainWindow.init_cam()

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
        if(i % 20 == 0):
            # print("------add figure------")
            global_lat.append(lat_deg)
            global_lon.append(lon_deg)
            print(lat_deg, lon_deg)

async def refresh_airspd(drone:System, MainWindow):
    async for fixedwingmetrics in drone.telemetry.fixedwing_metrics():
        # print(fixedwingmetrics)
        speed = round(fixedwingmetrics.airspeed_m_s, 2)
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
    tasks = [refresh_airspd(drone, MainWindow), refresh_position(drone, MainWindow), refresh_battery(drone, MainWindow), refresh_flightmode(drone, MainWindow)]
    loop.run_until_complete(asyncio.wait(tasks))

def auto_bomb_begin():
    global auto_bomb_flag
    auto_bomb_flag = True

def auto_bomb_end():
    global auto_bomb_flag
    auto_bomb_flag = False