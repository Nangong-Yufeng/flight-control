#!/usr/bin/env python3

import asyncio
import pygame
import numpy as np

from mavsdk import System
from mavsdk.mission import *
from mavsdk.offboard import (ActuatorControl, ActuatorControlGroup, OffboardError, Attitude, )

pygame.init()
window = pygame.display.set_mode((300, 300))  # 启动pygame进行按键监听

drone = System()
pos = [[22.58927, 113.96436], [22.58739, 113.96771],
       [22.58680, 113.96645]]  # 设置标靶坐标, 这个是为了goto使用的, 但goto已经被抛弃, 所以它也可以删掉
pos = np.array(pos)

# 设置侦察任务
scout_mission = [MissionItem(22.58927,
                             113.96436,
                             25,
                             10,
                             True,
                             0,
                             float('nan'),
                             MissionItem.CameraAction.NONE,
                             float('nan'),
                             float('nan'),
                             float('nan'),
                             float('nan'),
                             float('nan')), MissionItem(22.58739,
                                                        113.96771,
                                                        25,
                                                        10,
                                                        True,
                                                        90,
                                                        float('nan'),
                                                        MissionItem.CameraAction.NONE,
                                                        float('nan'),
                                                        float('nan'),
                                                        float('nan'),
                                                        float('nan'),
                                                        float('nan')), MissionItem(22.58680,
                                                                                   113.96645,
                                                                                   25,
                                                                                   10,
                                                                                   True,
                                                                                   -90,
                                                                                   float('nan'),
                                                                                   MissionItem.CameraAction.NONE,
                                                                                   float('nan'),
                                                                                   float('nan'),
                                                                                   float('nan'),
                                                                                   float('nan'),
                                                                                   float('nan'))]

# 设置打击任务1
bomb1 = [MissionItem(22.58927,
                     113.96436,
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

# 设置打击任务2
bomb2 = [MissionItem(22.58739,
                     113.96771,
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

# 设置打击任务3
bomb3 = [MissionItem(22.58680,
                     113.96645,
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


async def setup():  # 初始化drone, 连接和检查
    """
    General configurations, setups, and connections are done here.
    :return:
    """
    global drone
    print("connect begin")
    await drone.connect(system_address="serial:///dev/ttyUSB0")
    # await drone.connect(system_address="udp://:14540")

    print("connect end")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"Drone discovered!")
            break

    # print("Waiting for drone to have a global position estimate...")
    # async for health in drone.telemetry.health():
    #     if health.is_global_position_ok:
    #         print("Global position estimate ok")
    #         break


async def main():  # main函数, 进行监听和任务分配
    global drone
    running = True

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # While being in air and landing mode the drone is not likely to takeoff again, so
        # a condition check is required here to avoid such a condition.

        if keys[pygame.K_UP] and (await print_in_air(drone) != True):  # 按 上 起飞
            print("takeoff begin")
            await takeoff()
            print("takeoff end")

        elif keys[pygame.K_DOWN]:  # 按 下 降落
            print("land begin")
            await land()
            print("land end")

        elif keys[pygame.K_m] and (await print_in_air(drone) == True):  # 按 m 进入侦察任务
            print("scout begin")
            await runMission(scout_mission, False)
            print("scout end")

        elif keys[pygame.K_1] and (await print_in_air(drone) == True):  # 按 1 前往打击点1
            print("bomb1 begin")
            if not await drone.mission.is_mission_finished():
                await drone.mission.pause_mission()
                await drone.mission.clear_mission()
            await runMission(bomb1, True)
            print("bomb1 end")

        elif keys[pygame.K_2] and (await print_in_air(drone) == True):  # 按 2 前往打击点2
            print("bomb2 begin")
            if not await drone.mission.is_mission_finished():
                await drone.mission.pause_mission()
                await drone.mission.clear_mission()
            await runMission(bomb2, True)
            print("bomb2 end")

        elif keys[pygame.K_3] and (await print_in_air(drone) == True):  # 按 3 前往打击点3
            print("bomb3 begin")
            if not await drone.mission.is_mission_finished():
                await drone.mission.pause_mission()
                await drone.mission.clear_mission()
            await runMission(bomb3, True)
            print("bomb3 end")

        elif keys[pygame.K_RIGHT]:  # 按 右 打印是否在空中
            await print_in_air(drone)

        elif keys[pygame.K_i]:  # 按 i 打印 电池, 是否在空中, gps, 位置信息
            await info(drone)

        elif keys[pygame.K_r]:  # 按r打印以度为单位的侧倾角，正值向右倾斜
            await print_roll_deg(drone)

        elif keys[pygame.K_a]:
            # await run_actuator()
            await drone.action.arm()
        elif keys[pygame.K_PAGEUP]:
            await set_actuator_1(drone)
        elif keys[pygame.K_PAGEDOWN]:
            await set_actuator_f1(drone)


# 被抛弃的goto_location函数
# async def goto(target):  # it's useless
#     global drone
#     if not await drone.mission.is_mission_finished():
#         await drone.mission.pause_mission()
#     print("Going to", end=" ")
#     print(target)
#     await drone.action.goto_location(target[0], target[1], 50, 0)


async def takeoff():
    """
    Default takeoff command seperated and taken from takeoff_and_land.py
    :return:
    """

    print("-- Arming")
    await drone.action.arm()

    print("-- Taking off")
    await drone.action.takeoff()


async def land():
    """
    Default land command seperated and taken from takeoff_and_land.py
    :return:
    """

    await drone.action.land()


async def info(drone=drone):
    """
    This is the combination of the print_battery, print_in_air, print_gps_info, and print_position functions aimed
    to display all of the counted data/information at the same exact time.
    :param drone:
    :return:
    """

    await print_battery(drone)
    await print_in_air(drone)
    await print_gps_info(drone)
    await print_position(drone)

    return True


async def print_in_air(drone=drone):
    async for in_air in drone.telemetry.in_air():
        print(f"In air: {in_air}")
        return in_air


async def print_battery(drone=drone):
    """
    Default print_battery command seperated and taken from telemetry.py
    :param drone:
    :return:
    """

    async for battery in drone.telemetry.battery():
        print(f"Battery: {battery.remaining_percent}")
        return battery.remaining_percent


async def print_gps_info(drone=drone):
    """
    Default print_gps_info command seperated and taken from telemetry.py
    :param drone:
    :return:
    """

    async for gps_info in drone.telemetry.gps_info():
        print(f"GPS info: {gps_info}")
        return gps_info


async def print_position(drone=drone):
    """
    Default print_position command seperated and taken from telemetry.py
    :param drone:
    :return:
    """

    async for position in drone.telemetry.position():
        print(position)
        return position


async def runMission(mission_items, is_back):
    global drone

    # print_mission_progress_task = asyncio.ensure_future(
    #     print_mission_progress(drone))

    # running_tasks = [print_mission_progress_task]
    termination_task = asyncio.ensure_future(
        observe_is_in_air(drone))

    mission_plan = MissionPlan(mission_items)

    await drone.mission.set_return_to_launch_after_mission(is_back)

    print("-- Uploading mission")
    await drone.mission.upload_mission(mission_plan)

    print("-- Arming")
    await drone.action.arm()

    print("-- Starting mission")
    await drone.mission.start_mission()

    await termination_task


async def observe_is_in_air(drone):
    """ Monitors whether the drone is flying or not and
    returns after landing """

    was_in_air = False
    was_mission_finished = False
    is_mission_finished = False

    async for mission_progress in drone.mission.mission_progress():
        print(f"Mission progress: "
              f"{mission_progress.current}/"
              f"{mission_progress.total}")
        await info(drone)

        if mission_progress.current == mission_progress.total:
            print("is_mission_finished = True")
            is_mission_finished = True

        if not was_mission_finished and is_mission_finished:
            await asyncio.get_event_loop().shutdown_asyncgens()
            return


async def print_roll_deg(drone):
    async for euler_angle in drone.telemetry.attitude_euler():
        roll_deg = euler_angle.roll_deg
        print(f"roll: {roll_deg}")
        return roll_deg


async def run_actuator():
    """ Does Offboard control using attitude commands. """

    global drone
    # drone = System()

    # await drone.connect(system_address="udp://:14540")
    # await drone.connect(system_address="serial:///dev/ttyUSB0")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"Drone discovered!")
            break

    print("-- Arming")
    await drone.action.arm()
    await asyncio.sleep(5)
    group0 = ActuatorControlGroup([
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    ])
    group2 = ActuatorControlGroup([
        0.1,
        0.1,
        0.1,
        0.1,
        0.1,
        0.1,
        0.1,
        0.1,
    ])
    await drone.offboard.set_attitude(
        Attitude(0.0, 0.0, 0.0, 0.0)
    )

    print("-- Starting offboard")
    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(f"Starting offboard mode failed with error code: \
              {error._result.result}")
        print("-- Disarming")
        await drone.action.disarm()
        return

    # asyncio.ensure_future(set_actuator_command(drone))
    print("-- Set zero att")
    await asyncio.sleep(50.0)

    print("-- Stopping offboard")
    try:
        await drone.offboard.stop()
    except OffboardError as error:
        print(f"Stopping offboard mode failed with error code: \
              {error._result.result}")


async def set_actuator_command(drone):
    async for euler_angle in drone.telemetry.attitude_euler():
        roll_deg = euler_angle.roll_deg  # 以度为单位的侧倾角，正值向右倾斜
        print(f"roll: {roll_deg}")
        scale = (roll_deg * 4) / 360
        print(f"scale: {scale}")
        group1 = ActuatorControlGroup([
            float('nan'),
            float('nan'),
            float('nan'),
            float('nan'),
            scale,
            scale,
            scale,
            scale,
        ])
        group0 = group1
        await drone.offboard.set_actuator_control(ActuatorControl([
            group1,
            group0,
        ]))
        await asyncio.sleep(0.01)


async def set_actuator_1(drone):
    print("set_actuator_1 begin")
    await drone.action.set_actuator(1, 0.9)
    print("set_actuator_1 end")


async def set_actuator_f1(drone):
    print("set_actuator_f1 begin")
    await drone.action.set_actuator(1, -0.9)
    print("set_actuator_f1 end")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup())
    loop.run_until_complete(main())
