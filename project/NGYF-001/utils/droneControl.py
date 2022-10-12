import asyncio
import sys
import threading
import folium
from folium.features import DivIcon
from mavsdk import System

async def my_mission(drone:System, mission_items, threshold): # add para threshold
    # mission_items[]: lot of mission_item
    # mission_item[0]: lat_deg
    # mission_item[1]: lon_deg
    # mission_item[2]: rel_alt
    # mission_item[3]: speed
    print('设置参数为1m')
    await drone.param.set_param_float('NAV_LOITER_RAD', 1)
    print('参数设置成功')
    # print('正在读取飞机当前高度')
    # plane_abs_alt = await get_abs_alt(drone)
    # print('高度读取成功，当前高度', plane_abs_alt, '米')
    i = 0
    total = len(mission_items)
    for mission_item in mission_items:
        i = i+1
        print('--开始导航到目标点 (', i, '/', total, ')')
        now_position = [drone.lat, drone.lon]
        print('=======',now_position[0], now_position[1], mission_item[0], mission_item[1],'=======')
        total_dist = dis([now_position[0], now_position[1]], [mission_item[0], mission_item[1]])
        await drone.param.set_param_float('FW_AIRSPD_TRIM', mission_item[3])
        await drone.action.goto_location(mission_item[0], mission_item[1], drone.landalt + mission_item[2], 0)
        
        print('--导航中 (', i, '/', total, ')')    
        await waiting_to_waypoint(drone, mission_item, total_dist, i, total, threshold) # add para threshold
    print('导航结束！')
    print('设置参数为默认')
    await drone.param.set_param_float('NAV_LOITER_RAD', 25)
    print('参数设置成功')
    # track_display_thread = threading.Thread(target=track_display, args=(loop, drone)) # put to main
    # track_display_thread.start() # put to main

async def waiting_to_waypoint(drone:System, waypoint, total_dist, i, total, threshold):
    # global lat_deg, lon_deg, abs_alt, rel_alt, Map
    last_lon = 0.0
    last_lat = 0.0
    last_process = 0
    refresh_i = 0
    while True:
        
        if(drone.lon == last_lon and drone.lat == last_lat):
            continue
        # print('now drone position = ', drone.lat, drone.lon)
        last_lon = drone.lon
        last_lat = drone.lat
        now_dist = dis([drone.lat, drone.lon], [waypoint[0], waypoint[1]])
        print('now dist/total dist: ', now_dist, '/', total_dist)
        now_process = round((total_dist - now_dist + threshold) / total_dist * 100)
        if(last_process != now_process):
            print('--当前进度', now_process, '%')
            # print("\r", end="")
            # print("导航点({}/{})进度: {}%: ".format(i, total, now_process), "▋" * (now_process // 2), end="")
            # sys.stdout.flush()
        if(((now_dist) < threshold) or (now_process>90 and now_process<last_process)):  # 飞机位置与目标点距离小于threshold米或开始套圈
            print('--到达目标点 (', i, '/', total, ')')
            return
        last_process = now_process
    # async for position in drone.telemetry.position():
    #     refresh_i = refresh_i + 1
    #     lat_deg = round(position.latitude_deg, 7)
    #     lon_deg = round(position.longitude_deg, 7)
    #     abs_alt = round(position.absolute_altitude_m, 2)
    #     rel_alt = round(position.relative_altitude_m, 2)

    #     now_dist = dis([lat_deg, lon_deg], [waypoint[0], waypoint[1]])
    #     now_process = round((total_dist - now_dist + threshold) / total_dist * 100)
    #     if(last_process != now_process):
    #         # print('--当前进度', now_process, '%')
    #         print("\r", end="")
    #         print("导航点({}/{})进度: {}%: ".format(i, total, now_process), "▋" * (now_process // 2), end="")
    #         sys.stdout.flush()
    #     if(now_dist) < threshold:  # 飞机位置与目标点距离小于threshold米
    #         print('--到达目标点 (', i, '/', total, ')')
    #         return
    #     last_process = now_process
    #     if(refresh_i % 5 == 0):
    #         track.append([lat_deg, lon_deg])
    #         folium.PolyLine(locations=track, color='#DC143C', weight = 2).add_to(Map)

# async def get_abs_alt(drone:System):
#     async for position in drone.telemetry.position():
#         return position.absolute_altitude_m

# async def get_position(drone:System):
#     async for position in drone.telemetry.position():
#         return position

def dis(point0, point1):
    return ((point0[0]-point1[0])**2 + (point0[1]-point1[1])**2)**0.5

def plan_route(boundary, Map, mission_route, mission_Items):  # 默认给出四点边界
    # global mission_route, mission_Items
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
    n = int(min(dist0/0.00015, dist1/0.00015))
    # print('n = ', n)
    mod0 = dist0%0.00015
    mod1 = dist1%0.00015
    group0_now = [group0[0][0]+(group0[1][0]-group0[0][0])*mod0/(2*dist0), group0[0][1]+(group0[1][1]-group0[0][1])*mod0/(2*dist0)]
    group1_now = [group1[0][0]+(group1[1][0]-group1[0][0])*mod1/(2*dist1), group1[0][1]+(group1[1][1]-group1[0][1])*mod1/(2*dist1)]
    sin0 = (group0[1][1]-group0[0][1])/dist0
    cos0 = (group0[1][0]-group0[0][0])/dist0
    sin1 = (group1[1][1]-group1[0][1])/dist1
    cos1 = (group1[1][0]-group1[0][0])/dist1
    # mission_route.append(group0_now)
    # group0_now = [group0_now[0]+0.0005*cos0, group0_now[1]+0.0005*sin0]
    i = 0
    while i < n:
        # if(i % 2 == 0):
        #     mission_route.append(group1_now)
        #     group1_temp = [group1_now[0]+0.0005*cos1, group1_now[1]+0.0005*sin1]
        #     mission_route.append(group1_temp)
        #     group0_temp = [group0_now[0]+0.0005*cos0, group0_now[1]+0.0005*sin0]
        #     mission_route.append(group0_temp)
        #     group1_now = [group1_now[0]+0.0001*cos1, group1_now[1]+0.0001*sin1]
        # else:
        #     # mission_route.append(group0_now)
        #     group0_now = [group0_now[0]+0.0001*cos0, group0_now[1]+0.0001*sin0]
        #     mission_route.append(group0_now)
        #     group0_now = [group0_now[0]+0.0005*cos0, group0_now[1]+0.0005*sin0]
        mission_route.append(group0_now)
        mission_route.append(group1_now)
        group1_temp = [group1_now[0]+0.00065*cos1, group1_now[1]+0.00065*sin1]
        mission_route.append(group1_temp)
        group0_temp = [group0_now[0]+0.00065*cos0, group0_now[1]+0.00065*sin0]
        mission_route.append(group0_temp)
        group0_now = [group0_now[0]+0.00015*cos0, group0_now[1]+0.00015*sin0]
        group1_now = [group1_now[0]+0.00015*cos1, group1_now[1]+0.00015*sin1]
        i = i+1
    # if(i % 2 == 0):
    #     mission_route.append(group1_now)
    # else:
    #     mission_route.append(group0_now)
    mission_route.append(group0_now)
    mission_route.append(group1_now)
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
        mission_Items.append([point[0], point[1], 40, 12])
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
