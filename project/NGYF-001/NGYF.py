from audioop import add
from cgitb import html
from cmath import sqrt
from email.charset import add_alias
from json import load
import threading
from tokenize import group
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
import sys
import os
import folium
from folium.features import DivIcon


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
Map = folium.Map(location=[22.590719999999997, 113.97554149999999],
                 max_zoom=19, 
                 zoom_start=18,
                 crs="EPSG3857", 
                 control_scale=True,
                 tiles = 'OpenStreetMap',  # 使用OpenStreetMap
                 attr='default')

Map.add_child(folium.LatLngPopup())                     # 显示鼠标点击点经纬度
# Map.add_child(folium.ClickForMarker(popup='Waypoint'))  # 将鼠标点击点添加到地图上

Map.save("save_map.html")

path = "file:\\" + os.getcwd() + "\\save_map.html"
path = path.replace('\\', '/')

class MainWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.setWindowTitle('NGYF-001')
        self.resize(1920, 1080)
        # 新建一个QWebEngineView()对象
        self.qwebengine = QWebEngineView(self)
        # 设置网页在窗口中显示的位置和大小
        self.qwebengine.setGeometry(0, 0, 1920, 1080)
        # 在QWebEngineView中加载网址
        # path = "file:\\" + os.getcwd() + "\\save_map.html"
        # path = path.replace('\\', '/')
        # self.qwebengine.load(QUrl(path))
        self.loadMap()
    
    def loadMap(self):
        path = "file:\\" + os.getcwd() + "\\save_map.html"
        path = path.replace('\\', '/')
        self.qwebengine.load(QUrl(path))

def route_plan(boundary, win:MainWindow):  # 默认给出四点边界
    
    mission_route = []
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
    print(dist)
    group0.sort(key=lambda x:x[0]**2+x[1]**2)
    group1.sort(key=lambda x:x[0]**2+x[1]**2)
    print('group0 = ', group0)
    print('group1 = ', group1)
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
    Map.save("save_map.html")
    dist0 = dis(group0[0], group0[1])
    dist1 = dis(group1[0], group1[1])
    n = int(min(dist0/0.0005, dist1/0.0005))
    print('n = ', n)
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
    folium.PolyLine(locations=mission_route, popup=folium.Popup('预计航线', max_width=200), color='#14DCB4').add_to(Map)
    Map.save("save_map.html")

def dis(point0, point1):
    return ((point0[0]-point1[0])**2 + (point0[1]-point1[1])**2)**0.5

if __name__ == '__main__':
    boundary = [[22.5909, 113.9757], [22.5909, 113.9750], [22.5899, 113.9757], [22.5899, 113.9750]]
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    threading.Thread(target=route_plan, args=(boundary, win)).start()
    sys.exit(app.exec_())

