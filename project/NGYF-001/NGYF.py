from audioop import add
from cgitb import html
from cmath import sqrt
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
from mavsdk import System
from mavsdk.mission import *
import nest_asyncio


init_mavsdk_server = r'"sources\mavsdk-windows-x64-release\bin\mavsdk_server_bin.exe -p 50051 serial://COM3:57600"' # 你要运行的exe文件
mission_route = []
mission_Items = [[22.5904, 113.9754, 80, 13]]
# land_mission_Items = [MissionItem(22.5912,
#                                                    113.9753,
#                                                     10,
#                                                     10,
#                                                     True,
#                                                     float('nan'),
#                                                     float('nan'),
#                                                     MissionItem.CameraAction.NONE,
#                                                     float('nan'),
#                                                     float('nan'),
#                                                     float('0.1'),
#                                                     float('nan'),
#                                                     float('nan')), 
#                                                     MissionItem(22.5909,
#                                                     113.9753,
#                                                     5,
#                                                     10,
#                                                     True,
#                                                     float('nan'),
#                                                     float('nan'),
#                                                     MissionItem.CameraAction.NONE,
#                                                     float('nan'),
#                                                     float('nan'),
#                                                     float('0.1'),
#                                                     float('nan'),
#                                                     float('nan')), 
#                                                     MissionItem(22.5905,
#                                                     113.9753,
#                                                     2,
#                                                     7,
#                                                     True,
#                                                     float('nan'),
#                                                     float('nan'),
#                                                     MissionItem.CameraAction.NONE,
#                                                     float('nan'),
#                                                     float('nan'),
#                                                     float('0.1'),
#                                                     float('nan'),
#                                                     float('nan'))]
land_mission_Items = [[22.5912,113.9753,10,10], [22.5909, 113.9753, 5, 10], [22.5905, 113.9753, 2,7]]
goto_test_item = [22.5909, 113.9751, 40]
track = []
lat_deg = -1.0
lon_deg = -1.0
abs_alt = -1.0
rel_alt = -1.0
land_alt = -1.0
threshold = 0.00010  # 阈值10m


nest_asyncio.apply()
# 标记实心圆
def add_red_marker(Map, location):
    folium.CircleMarker(
        location=[location[0], location[1]],
        radius=5,
        popup='popup',
        color='#DC143C',      # 圈的颜色
        fill=True,
        fill_color='#6495E'  # 填充颜色
    ).add_to(Map)
    return Map

def add_blue_marker(Map, location):
    folium.CircleMarker(
        location=[location[0], location[1]],
        radius=5,
        popup='popup',
        color='#142BDC',      # 圈的颜色
        fill=True,
        fill_color='#6495E'  # 填充颜色
    ).add_to(Map)
    return Map

# 调用高德地图http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}
Map = folium.Map(location=[22.5904, 113.9754],
                 max_zoom=19, 
                 zoom_start=19,
                 crs="EPSG3857",
                 control_scale=True,
                 tiles = 'OpenStreetMap',  # 使用OpenStreetMap
                 attr='default')

Map.add_child(folium.LatLngPopup())                     # 显示鼠标点击点经纬度
# Map.add_child(folium.ClickForMarker(popup='Waypoint'))  # 将鼠标点击点添加到地图上

Map.save("save_map.html")


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
        self.pushButton02.setText("降落")

        self.pushButton00.clicked.connect(lambda: save(self))
        self.pushButton01.clicked.connect(lambda: mission_part(self.loop, self.drone, mission_Items))
        self.pushButton02.clicked.connect(lambda:land_part(self.loop, self.drone))
    
    def loadMap(self):
        path = "file:\\" + os.getcwd() + "\\save_map.html"
        path = path.replace('\\', '/')
        self.qwebengine.load(QUrl(path))

def route_plan(boundary):  # 默认给出四点边界
    global mission_route, mission_Items
    print('生成航线中···')
    # mission_route = []
    dist = [9, 9, 9]
    dist[0] = ((boundary[0][0]-boundary[1][0])**2 + (boundary[0][1]-boundary[1][1])**2)**0.5  # 0.001是100m
    dist[1] = ((boundary[0][0]-boundary[2][0])**2 + (boundary[0][1]-boundary[2][1])**2)**0.5
    dist[2] = ((boundary[0][0]-boundary[3][0])**2 + (boundary[0][1]-boundary[3][1])**2)**0.5
    # print(dist.index(min(dist)) + 1, '和 0')
    group0 = [boundary[0], boundary[dist.index(min(dist)) + 1]]
    group1 = []
    for i in range(1, 4):
        if(i != dist.index(min(dist)) + 1):
            group1.append(boundary[i])
    # dist.sort()
    # print(dist)
    group0.sort(key=lambda x:x[0]**2+x[1]**2)
    group1.sort(key=lambda x:x[0]**2+x[1]**2)
    # print('group0 = ', group0)
    # print('group1 = ', group1)
    add_red_marker(Map, group0[0])
    add_red_marker(Map, group0[1])
    add_blue_marker(Map, group1[0])
    add_blue_marker(Map, group1[1])
    folium.Polygon(
        locations=[group0[0], group0[1], group1[1], group1[0]],
        popup=folium.Popup('坐标点之间多边形区域', max_width=200),
        color='blue', # 线颜色
        fill=True, # 是否填充
        weight=3, # 边界线宽
    ).add_to(Map)
    # Map.save("save_map.html")
    dist0 = dis(group0[0], group0[1])
    dist1 = dis(group1[0], group1[1])
    n = int(min(dist0/0.0005, dist1/0.0005))
    # print('n = ', n)
    mod0 = dist0%0.0005
    mod1 = dist1%0.0005
    group0_now = [group0[0][0]+(group0[1][0]-group0[0][0])*mod0/(2*dist0), group0[0][1]+(group0[1][1]-group0[0][1])*mod0/(2*dist0)]
    group1_now = [group1[0][0]+(group1[1][0]-group1[0][0])*mod1/(2*dist1), group1[0][1]+(group1[1][1]-group1[0][1])*mod1/(2*dist1)]
    sin0 = (group0[1][1]-group0[0][1])/dist0
    cos0 = (group0[1][0]-group0[0][0])/dist0
    sin1 = (group1[1][1]-group1[0][1])/dist1
    cos1 = (group1[1][0]-group1[0][0])/dist1
    mission_route.append(group0_now)
    group0_now = [group0_now[0]+0.0005*cos0, group0_now[1]+0.0005*sin0]
    i = 0
    while i < n:
        if(i % 2 == 0):
            mission_route.append(group1_now)
            group1_now = [group1_now[0]+0.0005*cos1, group1_now[1]+0.0005*sin1]
            mission_route.append(group1_now)
            group1_now = [group1_now[0]+0.0005*cos1, group1_now[1]+0.0005*sin1]
        else:
            mission_route.append(group0_now)
            group0_now = [group0_now[0]+0.0005*cos0, group0_now[1]+0.0005*sin0]
            mission_route.append(group0_now)
            group0_now = [group0_now[0]+0.0005*cos0, group0_now[1]+0.0005*sin0]
        i = i+1
    if(i % 2 == 0):
        mission_route.append(group1_now)
    else:
        mission_route.append(group0_now)
    mission_route.append([22.5904, 113.9754])
    print('航线生成成功！')
    print('mission_route = ', mission_route)
    i = 1
    for point in mission_route:
        folium.CircleMarker(
            location=point,
            radius=3,
            popup='popup',
            color='#14DCB4',      # 圈的颜色
            fill=True,
            fill_color='#6495E'  # 填充颜色
        ).add_to(Map)
        folium.map.Marker(
        point,
        icon=DivIcon(
            icon_size=(250,36),
            icon_anchor=(0,0),
            html='<div style="font-size: 20pt">'+str(i)+'</div>',
            )
        ).add_to(Map)
        i = i+1
        # mission_Items.append([point[0], point[1], 20, 10])
    print('任务生成成功! ', mission_Items)
    folium.PolyLine(locations=mission_route, popup=folium.Popup('预计航线', max_width=200), color='#14DCB4').add_to(Map)

def dis(point0, point1):
    return ((point0[0]-point1[0])**2 + (point0[1]-point1[1])**2)**0.5

def open_mavsdk_server():
        server = os.system(init_mavsdk_server)
        print (server)


def connect_plane(loop, drone):
    print('连接飞机中···')
    loop.run_until_complete(drone_connect(drone))

async def drone_connect(drone):
    # await drone.connect(system_address="udp://:14540")
    await drone.connect()
    print('飞机连接成功！')

def track_display(loop, drone):
    print('开启航迹显示中···')
    loop.run_until_complete(refresh_position(drone))

def save(win:MainWindow):
    global track
    try: 
        track = []
        Map.save("save_map.html")
        win.loadMap()
    except:
        print('地图刷新失败')

async def refresh_position(drone):
    global lat_deg, lon_deg, abs_alt, rel_alt, land_alt, Map
    Map.save("save_map.html")
    i = 0
    async for position in drone.telemetry.position():
        # print(position)
        i = i+1
        lat_deg = round(position.latitude_deg, 7)
        lon_deg = round(position.longitude_deg, 7)
        abs_alt = round(position.absolute_altitude_m, 2)
        rel_alt = round(position.relative_altitude_m, 2)
        # print(lat_deg, lon_deg)
        if(i == 1):
            land_alt = abs_alt - rel_alt
        if(i % 2 == 0):
            track.append([lat_deg, lon_deg])
            folium.PolyLine(locations=track, color='#DC143C', weight = 2).add_to(Map)
    print('错误!  数据链断开!  错误!  数据链断开!  错误!  数据链断开!  ')


def land_part(loop, drone):
    threading.Thread(target=land, args=(loop, drone, land_mission_Items)).start()

def land(loop, drone, land_mission_items):
    loop.run_until_complete(land_drone(drone, land_mission_items))

async def land_drone(drone:System, land_mission_items):
    print('--开始降落')
    await my_mission_drone(drone, land_mission_items)
    print('--准备着陆')
    await drone.action.land()
    print('--降落成功')

def mission_part(loop, drone, mission_items):
    threading.Thread(target=mission, args=(loop, drone, mission_items)).start()

def mission(loop, drone, mission_items):
    loop.run_until_complete(my_mission_drone(drone, mission_items))

async def my_mission_drone(drone:System, mission_items):
    # mission_item[0]: lat_deg
    # mission_item[1]: lon_deg
    # mission_item[2]: rel_alt
    # mission_item[3]: speed
    print('设置参数为1m')
    await drone.param.set_param_float('NAV_LOITER_RAD', 1)
    print('参数设置成功')
    print('正在读取飞机当前高度')
    plane_abs_alt = await get_abs_alt(drone)
    print('高度读取成功，当前高度', plane_abs_alt, '米')
    i = 0
    total = len(mission_items)
    for mission_item in mission_items:
        i = i+1
        print('--开始导航到目标点 (', i, '/', total, ')')
        now_position = await get_position(drone)
        total_dist = dis([now_position.latitude_deg, now_position.longitude_deg], [mission_item[0], mission_item[1]])
        await drone.param.set_param_float('FW_AIRSPD_TRIM', mission_item[3])
        await drone.action.goto_location(mission_item[0], mission_item[1], land_alt + mission_item[2], 0)
        
        print('--导航中 (', i, '/', total, ')')    
        await waiting_to_waypoint(drone, mission_item, total_dist, i, total)
    print('导航结束！')
    print('设置参数为默认')
    await drone.param.set_param_float('NAV_LOITER_RAD', 25)
    print('参数设置成功')
    track_display_thread = threading.Thread(target=track_display, args=(loop, drone))
    track_display_thread.start()

async def waiting_to_waypoint(drone:System, waypoint, total_dist, i, total):
    global lat_deg, lon_deg, abs_alt, rel_alt, Map
    last_process = 0
    refresh_i = 0
    async for position in drone.telemetry.position():
        refresh_i = refresh_i + 1
        lat_deg = round(position.latitude_deg, 7)
        lon_deg = round(position.longitude_deg, 7)
        abs_alt = round(position.absolute_altitude_m, 2)
        rel_alt = round(position.relative_altitude_m, 2)

        now_dist = dis([lat_deg, lon_deg], [waypoint[0], waypoint[1]])
        now_process = round((total_dist - now_dist + threshold) / total_dist * 100)
        if(last_process != now_process):
            # print('--当前进度', now_process, '%')
            print("\r", end="")
            print("导航点({}/{})进度: {}%: ".format(i, total, now_process), "▋" * (now_process // 2), end="")
            sys.stdout.flush()
        if((now_dist) < threshold) or (now_process>90 and now_process<last_process):  # 飞机位置与目标点距离小于threshold米, 或飞过目标点
            print('--到达目标点 (', i, '/', total, ')')
            return
        last_process = now_process
        if(refresh_i % 2 == 0):
            track.append([lat_deg, lon_deg])
            folium.PolyLine(locations=track, color='#DC143C', weight = 2).add_to(Map)

async def get_abs_alt(drone:System):
    async for position in drone.telemetry.position():
        return position.absolute_altitude_m

async def get_position(drone:System):
    async for position in drone.telemetry.position():
        return position

# async def mission_drone(drone, mission_items):
#     termination_task = asyncio.ensure_future(
#         observe_is_in_air(drone))

#     mission_plan = MissionPlan(mission_items)

#     await drone.mission.set_return_to_launch_after_mission(False)

#     print("-- Uploading mission")
#     await drone.mission.upload_mission(mission_plan)

#     print("-- Starting mission")
#     await drone.mission.start_mission()

#     await termination_task

# async def observe_is_in_air(drone):
#     """ Monitors whether the drone is flying or not and
#     returns after landing """

#     was_in_air = False
#     was_mission_finished = False
#     is_mission_finished = False

#     async for mission_progress in drone.mission.mission_progress():
#         print(f"Mission progress: "
#             f"{mission_progress.current}/"
#             f"{mission_progress.total}")

#         if mission_progress.current == mission_progress.total:
#             print("is_mission_finished = True")
#             is_mission_finished = True

#         if not was_mission_finished and is_mission_finished:
#             await asyncio.get_event_loop().shutdown_asyncgens()
#             return

if __name__ == '__main__':
    boundary = [[22.5909, 113.9757], [22.5909, 113.9750], [22.5899, 113.9757], [22.5899, 113.9750]]
    loop = asyncio.get_event_loop()
    drone = System(mavsdk_server_address='localhost', port=50051)
    app = QApplication(sys.argv)
    win = MainWindow(loop, drone)
    win.show()
    mavsdk_thread = threading.Thread(target=open_mavsdk_server).start()
    connect_plane_thread = threading.Thread(target=connect_plane, args=(loop, drone))
    connect_plane_thread.start()
    connect_plane_thread.join()
    route_plan_thread = threading.Thread(target=route_plan, args=(boundary, ))
    route_plan_thread.start()
    route_plan_thread.join()
    track_display_thread = threading.Thread(target=track_display, args=(loop, drone))
    track_display_thread.start()
    sys.exit(app.exec_())

