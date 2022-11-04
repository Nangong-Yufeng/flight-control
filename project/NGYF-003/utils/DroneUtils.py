import threading
import asyncio
import os
import nest_asyncio
from mavsdk.mission import *
from mavsdk import System
from PyQt5.QtWidgets import *

nest_asyncio.apply()
init_mavsdk_server = r'"sources\mavsdk-windows-x64-release\bin\mavsdk_server_bin.exe -p 50051 serial://COM3:57600"' # 你要运行的exe文件

def connect_plane(drone, loop):
        mavsdk_thread = threading.Thread(target=open_mavsdk_server)
        # mavsdk_thread.start()
        connect_thread = threading.Thread(target=connect_plane_thread, args=(drone, loop))
        connect_thread.start()

def open_mavsdk_server():
    server = os.system(init_mavsdk_server)
    print (server)

def connect_plane_thread(drone, loop):
    loop.run_until_complete(drone_connect(drone))

async def drone_connect(drone):
    # print('before connect')
    await drone.connect()
    print('connect success')

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

def scout_mission(drone, loop, waypoint_lists):
    scout_thread = threading.Thread(target=scout_mission_thread, args=(drone, loop, waypoint_lists))
    scout_thread.start()

def scout_mission_thread(drone, loop, waypoint_lists):
    # scout_mission = drone_control.get_scout_missions(tar_pos)
    loop.run_until_complete(mission_drone(drone, waypoint_lists))

async def mission_drone(drone: System, waypoint_lists):
    detect_flag = True
    i = 1
    
    while detect_flag:
        print_mission_progress_task = asyncio.ensure_future(
            print_mission_progress(drone, i))

        running_tasks = [print_mission_progress_task]
        termination_task = asyncio.ensure_future(
            observe_is_in_air(drone, running_tasks))

        # waypoint_lists = [
        #     [22.5917867, 113.9752335, 80, 12, 3],
        #     [22.5915777, 113.9755941, 80, 12, 3],
        #     [22.5912497, 113.9752591, 80, 12, 3],
        #     [22.5909264, 113.9752896, 80, 12, 1],
        #     [22.5904671, 113.9752947, 80, 12, 1],
        #     [22.5899377, 113.9753048, 80, 12, 1],
        #     [22.5896097, 113.9753099, 80, 12, 3],
        #     [22.5892395, 113.9757920, 80, 12, 3],
        #     [22.5888647, 113.9753353, 80, 12, 3],
        #     [22.5892067, 113.9749699, 80, 12, 3],
        #     [22.5896097, 113.9753099, 80, 12, 3],
        #     [22.5899377, 113.9753048, 80, 12, 1],
        #     [22.5904671, 113.9752947, 80, 12, 1],
        #     [22.5909264, 113.9752896, 80, 12, 1],
        #     [22.5912497, 113.9752591, 80, 12, 3],
        #     [22.5915214, 113.9748887, 80, 12, 3]
        # ]
        mission_items = generate_mission(waypoint_lists)

        mission_plan = MissionPlan(mission_items)

        await drone.mission.set_return_to_launch_after_mission(True)

        print("-- Uploading mission")
        await drone.mission.upload_mission(mission_plan)

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

def goto(drone, loop, i):
    gotothread = threading.Thread(target=goto_thread, args=(drone, loop, i))
    gotothread.start()

def goto_thread(drone, loop, i):
    loop.run_until_complete(goto_drone(drone, i))

async def goto_drone(drone:System, target):
    print("Have not completed yet")

def arm(drone, loop):
    armthread = threading.Thread(target=arm_thread, args=(drone, loop))
    armthread.start()

def arm_thread(drone, loop):
    loop.run_until_complete(arm_drone(drone))

async def arm_drone(drone: System):
    await drone.action.arm()

def disarm(drone, loop):
    disarmthread = threading.Thread(target=disarm_thread, args=(drone, loop))
    disarmthread.start()

def disarm_thread(drone, loop):
    loop.run_until_complete(disarm_drone(drone))

async def disarm_drone(drone: System):
    await drone.action.disarm()
    
# def kill(drone, loop, MainWindow):
#     reply = QMessageBox.question(MainWindow, 'kill?', '您想要自杀吗?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
#     if(reply == QMessageBox.Yes):
#         killthread = threading.Thread(target=kill_thread, args=(drone, loop))
#         killthread.start()

def kill_thread(drone, loop):
    loop.run_until_complete(kill_drone(drone))

async def kill_drone(drone:System):
    await drone.action.kill()

def drop_bomb(drone, loop):
    drop_bombthread = threading.Thread(target=drop_bomb_thread, args=(drone, loop))
    drop_bombthread.start()

def drop_bomb_thread(drone, loop):
    loop.run_until_complete(drop_bomb_drone(drone))

async def drop_bomb_drone(drone:System):
    await drone.action.set_actuator(1, 0.9)
    await asyncio.sleep(2)
    await drone.action.set_actuator(1, -0.9)

