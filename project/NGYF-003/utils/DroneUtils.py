import threading
import asyncio
import os
import nest_asyncio
from mavsdk.mission import *
from mavsdk import System
from PyQt5.QtWidgets import *
from UIutils import detect_flag, bomb_gps
# from pynput import keyboard


# get current state of roll axis (between -1 and 1)
roll = float(0)
# get current state of pitch axis (between -1 and 1)
pitch = float(0)
# get current state of throttle axis (between -1 and 1, but between 0 and 1 is expected)
throttle = float(0.5)
# get current state of yaw axis (between -1 and 1)
yaw = float(0)


nest_asyncio.apply()
init_mavsdk_server = r'"..\NantongYufeng\sources\mavsdk-windows-x64-release\bin\mavsdk_server_bin.exe -p 50051 serial://COM4:57600"' # 你要运行的exe文件
# init_mavsdk_server = r'"..\NantongYufeng\sources\mavsdk-windows-x64-release\bin\mavsdk_server_bin.exe -p 50051 udp://:14540"' # 你要运行的exe文件
def connect_plane(drone, loop):
        mavsdk_thread = threading.Thread(target=open_mavsdk_server)
        mavsdk_thread.start()
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

# def on_press(key):
    
#     global roll, pitch, throttle, yaw
    
#     if key == keyboard.Key.left:
#         roll = float(-0.7)
#     if key == keyboard.Key.right:
#         roll = float(0.7)
#     if key == keyboard.Key.up:
#         pitch = float(0.7)
#     if key == keyboard.Key.down:
#         pitch = float(-0.7)

#     if key == keyboard.KeyCode.from_char('w'):
#         if throttle < 1:
#             throttle = throttle + 0.1
#         print("== Set throttle {} ==".format(throttle))
#     if key == keyboard.KeyCode.from_char('s'):
#         if throttle > 0:
#             throttle = throttle - 0.1
#         print("== Set throttle {} ==".format(throttle))
#     if key == keyboard.KeyCode.from_char('a'):
#         yaw = float(-0.7)
#     if key == keyboard.KeyCode.from_char('d'):
#         yaw = float(0.7)    

#     print('Key %s pressed' % key) 
        
# def on_release(key):

#     global roll, pitch, throttle, yaw
    
#     if key == keyboard.Key.left:
#         roll = float(0)
#     if key == keyboard.Key.right:
#         roll = float(0)
#     if key == keyboard.Key.up:
#         pitch = float(0)
#     if key == keyboard.Key.down:
#         pitch = float(0)

#     if key == keyboard.KeyCode.from_char('w'):
#         throttle = throttle
#     if key == keyboard.KeyCode.from_char('s'):
#         throttle = throttle
#     if key == keyboard.KeyCode.from_char('a'):
#         yaw = float(0)
#     if key == keyboard.KeyCode.from_char('d'):
#         yaw = float(0)  

#     print('Key %s released' %key) 
#     if key == keyboard.Key.esc: # esc 키가 입력되면 종료 
#         return False

# def drone_keyboard():
#     with keyboard.Listener( on_press=on_press, on_release=on_release) as listener: 
#         listener.join()

# async def manual_controls(drone: System):
#     """Main function to connect to the drone and input manual controls"""
#     # Connect to the Simulation
#     # drone = System()
#     # drone = System(mavsdk_server_address='localhost', port=50051) # drone on windows
#     # await drone.connect(system_address="udp://:14540")

#     # # This waits till a mavlink based drone is connected
#     # async for state in drone.core.connection_state():
#     #     if state.is_connected:
#     #         print(f"-- Connected to drone with UUID: {state.uuid}")
#     #         break

#     # # Checking if Global Position Estimate is ok
#     # async for global_lock in drone.telemetry.health():
#     #     if global_lock.is_global_position_ok:
#     #         print("-- Global position state is ok")
#     #         break

#     # # set the manual control input after arming
#     # await drone.manual_control.set_manual_control_input(
#     #     float(0), float(0), float(0.5), float(0)
#     # )

#     # # Arming the drone
#     # print("-- Arming")
#     # await drone.action.arm()

#     # # Takeoff the vehicle
#     # print("-- Taking off")
#     # await drone.action.takeoff()
    
#     # await asyncio.sleep(10)

#     # set the manual control input after arming
#     await drone.manual_control.set_manual_control_input(
#         float(0), float(0), float(0.5), float(0)
#     )

#     # start manual control
#     print("-- Starting manual control")
#     # await drone.manual_control.start_altitude_control()

#     while True:
#         # print("im in")
#         await drone.manual_control.set_manual_control_input(pitch, roll, throttle, yaw)
#         print("set{}, {}, {}, {}".format(pitch, roll, throttle, yaw))
#         await asyncio.sleep(0.1)
#         QApplication.processEvents()


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
    scout_thread = threading.Thread(target=mission_thread, args=(drone, loop, waypoint_lists))
    scout_thread.start()
    waypoint_lists = [  [bomb_gps[0]-0.0017711, bomb_gps[1]-0.0008836],
                        [bomb_gps[0]-0.0007679, bomb_gps[1]-0.0003139],
                        [bomb_gps[0]-0.0004695, bomb_gps[1]-0.0001878],
                        [bomb_gps[0], bomb_gps[1]]]
    bomb_thread = threading.Thread(target=mission_thread, args=(drone, loop, waypoint_lists))
    bomb_thread.start()

def mission_thread(drone, loop, waypoint_lists):
    # scout_mission = drone_control.get_scout_missions(tar_pos)
    loop.run_until_complete(mission_drone(drone, waypoint_lists))

async def mission_drone(drone: System, waypoint_lists):
    i = 1
    if(len(waypoint_lists) == 4):
        i = 99
    while detect_flag:
        print_mission_progress_task = asyncio.ensure_future(
            print_mission_progress(drone, i))

        running_tasks = [print_mission_progress_task]
        termination_task = asyncio.ensure_future(
            observe_is_in_air(drone, running_tasks))


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
        if mission_progress.current == 4 and i == 99: 
            print("Bombing")
            await drop_bomb_drone(drone)


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
    await drone.action.set_actuator(1, -1)
    await asyncio.sleep(2)
    await drone.action.set_actuator(1, 1)

