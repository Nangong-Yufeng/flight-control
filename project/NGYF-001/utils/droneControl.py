import asyncio
import sys
import threading
import folium
import numpy as np
import os
from folium.features import DivIcon
from mavsdk import System
from mavsdk.mission import *

def track_display(loop, drone, track, Map):
    print('开启航迹显示中···')
    loop.run_until_complete(refresh_position(drone, track, Map))

async def refresh_position(drone, track, Map):
    global lat_deg, lon_deg, abs_alt, rel_alt, land_alt
    Map.save("save_map.html")
    i = 0
    async for position in drone.telemetry.position():
        i = i+1
        lat_deg = round(position.latitude_deg, 7)
        lon_deg = round(position.longitude_deg, 7)
        abs_alt = round(position.absolute_altitude_m, 2)
        rel_alt = round(position.relative_altitude_m, 2)
        if(i == 1):
            land_alt = abs_alt - rel_alt
            print(position)
        if(i % 2 == 0):
            track.append([lat_deg, lon_deg])
            folium.PolyLine(locations=track, color='#DC143C', weight = 2).add_to(Map)
    print('错误!  数据链断开!  错误!  数据链断开!  错误!  数据链断开!  ')


def open_mavsdk_server(init_mavsdk_server):
        server = os.system(init_mavsdk_server)
        print (server)

def generate_mission(waypoint_lists):
    # waypoint: [lat, lon, rel_alt, speed, acceptance_radius]
    mission_items = []
    for waypoint in waypoint_lists:
        mission_items.append(MissionItem(waypoint[0],
                                     waypoint[1],
                                     waypoint[2],
                                     waypoint[3],
                                     True,
                                     float('nan'),
                                     float('nan'),
                                     MissionItem.CameraAction.NONE,
                                     float('nan'),
                                     float('nan'),
                                     waypoint[4],
                                     float('nan'),
                                     float('nan')))
    return mission_items

def mission_part(loop, drone, mission_items):
    threading.Thread(target=mission, args=(loop, drone, mission_items)).start()

def mission(loop, drone, mission_items):
    loop.run_until_complete(mission_drone(drone, mission_items))

async def mission_drone(drone, mission_items):
    detect_flag = True # 标靶是否检测全的flag
    i = 1 # 用于记录侦察圈数

    while detect_flag:
        print_mission_progress_task = asyncio.ensure_future(
            print_mission_progress(drone, i))

        running_tasks = [print_mission_progress_task]
        termination_task = asyncio.ensure_future(
            observe_is_in_air(drone, running_tasks))

        mission_plan = MissionPlan(mission_items)
        await drone.mission.set_return_to_launch_after_mission(True)

        print("-- Uploading mission")
        await drone.mission.upload_mission(mission_plan)

        # print("-- Arming")
        # await drone.action.arm()

        print("-- Starting mission")
        await drone.mission.start_mission()

        await termination_task
        i += 1

async def print_mission_progress(drone:System, i):
    async for mission_progress in drone.mission.mission_progress():
        print(f"Round {i} Mission progress: "
              f"{mission_progress.current}/"
              f"{mission_progress.total}")

async def observe_is_in_air(drone:System, running_tasks):
    """ Monitors whether the drone is flying or not and
    returns after landing """

    was_in_air = False
    was_mission_finished = True

    async for is_in_air in drone.telemetry.in_air():
    # async for mission_progress in drone.mission.mission_progress():
        is_mission_finished = await drone.mission.is_mission_finished();
        if is_in_air:
            was_in_air = is_in_air
        if not is_mission_finished:
            was_mission_finished = is_mission_finished
        if (was_in_air and not is_in_air) or (is_mission_finished and not was_mission_finished):
            for task in running_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            await asyncio.get_event_loop().shutdown_asyncgens()

            return


def land_part(loop, drone, land_mission_Items):
    threading.Thread(target=land, args=(loop, drone, land_mission_Items)).start()

def land(loop, drone, land_mission_items):
    loop.run_until_complete(land_drone(drone, land_mission_items))

async def land_drone(drone:System, land_mission_items):
    print('--开始降落')
    await mission_drone(drone, land_mission_items)
    print('--准备着陆')
    await drone.action.land()
    print('--降落成功')


def dis(point0, point1):
    return ((point0[0]-point1[0])**2 + (point0[1]-point1[1])**2)**0.5

def plan_route(boundary, Map, mission_route, mission_Items):  # 默认给出四点边界
    # # global mission_route, mission_Items
    # print('生成航线中···')
    # # mission_route = []
    # dist = [9, 9, 9]
    # dist[0] = ((boundary[0][0]-boundary[1][0])**2 + (boundary[0][1]-boundary[1][1])**2)**0.5  # 0.001是100m
    # dist[1] = ((boundary[0][0]-boundary[2][0])**2 + (boundary[0][1]-boundary[2][1])**2)**0.5
    # dist[2] = ((boundary[0][0]-boundary[3][0])**2 + (boundary[0][1]-boundary[3][1])**2)**0.5
    # # print(dist.index(min(dist)) + 1, '和 0')
    # group0 = [boundary[0], boundary[dist.index(min(dist)) + 1]]
    # group1 = []
    # for i in range(1, 4):
    #     if(i != dist.index(min(dist)) + 1):
    #         group1.append(boundary[i])
    # # dist.sort()
    # # print(dist)
    # group0.sort(key=lambda x:x[0]**2+x[1]**2)
    # group1.sort(key=lambda x:x[0]**2+x[1]**2)
    # # print('group0 = ', group0)
    # # print('group1 = ', group1)
    # add_red_marker(Map, group0[0])
    # add_red_marker(Map, group0[1])
    # add_blue_marker(Map, group1[0])
    # add_blue_marker(Map, group1[1])
    # folium.Polygon(
    #     locations=[group0[0], group0[1], group1[1], group1[0]],
    #     popup=folium.Popup('坐标点之间多边形区域', max_width=200),
    #     color='blue', # 线颜色
    #     fill=True, # 是否填充
    #     weight=3, # 边界线宽
    # ).add_to(Map)
    # # Map.save("save_map.html")
    # dist0 = dis(group0[0], group0[1])
    # dist1 = dis(group1[0], group1[1])
    # n = int(min(dist0/0.00015, dist1/0.00015))
    # # print('n = ', n)
    # mod0 = dist0%0.00015
    # mod1 = dist1%0.00015
    # group0_now = [group0[0][0]+(group0[1][0]-group0[0][0])*mod0/(2*dist0), group0[0][1]+(group0[1][1]-group0[0][1])*mod0/(2*dist0)]
    # group1_now = [group1[0][0]+(group1[1][0]-group1[0][0])*mod1/(2*dist1), group1[0][1]+(group1[1][1]-group1[0][1])*mod1/(2*dist1)]
    # sin0 = (group0[1][1]-group0[0][1])/dist0
    # cos0 = (group0[1][0]-group0[0][0])/dist0
    # sin1 = (group1[1][1]-group1[0][1])/dist1
    # cos1 = (group1[1][0]-group1[0][0])/dist1
    # # mission_route.append(group0_now)
    # # group0_now = [group0_now[0]+0.0005*cos0, group0_now[1]+0.0005*sin0]
    # i = 0
    # while i < n:
    #     # if(i % 2 == 0):
    #     #     mission_route.append(group1_now)
    #     #     group1_temp = [group1_now[0]+0.0005*cos1, group1_now[1]+0.0005*sin1]
    #     #     mission_route.append(group1_temp)
    #     #     group0_temp = [group0_now[0]+0.0005*cos0, group0_now[1]+0.0005*sin0]
    #     #     mission_route.append(group0_temp)
    #     #     group1_now = [group1_now[0]+0.0001*cos1, group1_now[1]+0.0001*sin1]
    #     # else:
    #     #     # mission_route.append(group0_now)
    #     #     group0_now = [group0_now[0]+0.0001*cos0, group0_now[1]+0.0001*sin0]
    #     #     mission_route.append(group0_now)
    #     #     group0_now = [group0_now[0]+0.0005*cos0, group0_now[1]+0.0005*sin0]
    #     mission_route.append(group0_now)
    #     mission_route.append(group1_now)
    #     group1_temp = [group1_now[0]+0.00065*cos1, group1_now[1]+0.00065*sin1]
    #     mission_route.append(group1_temp)
    #     group0_temp = [group0_now[0]+0.00065*cos0, group0_now[1]+0.00065*sin0]
    #     mission_route.append(group0_temp)
    #     group0_now = [group0_now[0]+0.00015*cos0, group0_now[1]+0.00015*sin0]
    #     group1_now = [group1_now[0]+0.00015*cos1, group1_now[1]+0.00015*sin1]
    #     i = i+1
    # # if(i % 2 == 0):
    # #     mission_route.append(group1_now)
    # # else:
    # #     mission_route.append(group0_now)
    # mission_route.append(group0_now)
    # mission_route.append(group1_now)
    # print('航线生成成功！')
    # print('mission_route = ', mission_route)
    i = 1
    # print('###################################################')
    # mission_route = np.array(mission_Items)
    # mission_route = mission_route[::, 0:2]
    # mission_route = mission_route.tolist()
    # print('###################################################')
    for mission_item in mission_Items:
        mission_route.append(mission_item[0:2])
    print("mission_route = {}".format(mission_route))
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
        # mission_Items.append(MissionItem(point[0],
        #                                             point[1],
        #                                             20,
        #                                             10,
        #                                             True,
        #                                             float('nan'),
        #                                             float('nan'),
        #                                             MissionItem.CameraAction.NONE,
        #                                             float('nan'),
        #                                             float('nan'),
        #                                             float('0.1'),
        #                                             float('nan'),
        #                                             float('nan')))
        # mission_Items.append([point[0], point[1], 40, 12])
    folium.PolyLine(locations=mission_route, popup=folium.Popup('预计航线', max_width=200), color='#14DCB4').add_to(Map)

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
