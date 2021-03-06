#!/usr/bin/env python3

import asyncio

import mavsdk.info
import pygame
import pygame_button
import numpy as np

from mavsdk import System
from mavsdk.mission import *
from mavsdk.offboard import (ActuatorControl, ActuatorControlGroup, OffboardError, Attitude, )

drone = System()
pos = [[22.58927, 113.96436], [22.58739, 113.96771],
       [22.58680, 113.96645]]  # 设置标靶坐标, 这个是为了goto使用的, 但goto已经被抛弃, 所以它也可以删掉
pos = np.array(pos)

takeoffCommand = False
landCommand = False
missionCommand = False
target1Command = False
target2Command = False
target3Command = False
refreshCommand = False

pygame.init()
display = pygame.display.set_mode((900, 600))  # 启动pygame进行按键监听
pygame.display.set_caption("nantongyufeng")

btn_takeoff = pygame_button.button(display, (0, 255, 0), "Takeoff", (25, 25, 150, 50), lambda: takeoffControl(),
                                   border_radius=5, font_family="Arial", font_size=18)

btn_land = pygame_button.button(display, (0, 255, 0), "Land", (225, 25, 150, 50), lambda: landControl(),
                                border_radius=5, font_family="Arial", font_size=18)

btn_mission = pygame_button.button(display, (0, 255, 0), "Scout Mission", (25, 125, 350, 50), lambda: missionControl(),
                                   border_radius=5, font_family="Arial", font_size=18)

btn_target1 = pygame_button.button(display, (0, 255, 0), "Target 1", (25, 225, 100, 50), lambda: target1Control(),
                                   border_radius=5, font_family="Arial", font_size=18)

btn_target2 = pygame_button.button(display, (0, 255, 0), "Target 2", (150, 225, 100, 50), lambda: target2Control(),
                                   border_radius=5, font_family="Arial", font_size=18)

btn_target3 = pygame_button.button(display, (0, 255, 0), "Target 3", (275, 225, 100, 50), lambda: target3Control(),
                                   border_radius=5, font_family="Arial", font_size=18)

btn_refresh = pygame_button.button(display, (0, 255, 0), "Refresh Info", (25, 325, 350, 50), lambda: refreshControl(),
                                   border_radius=5, font_family="Arial", font_size=18)

flightmode = "NULL"
battery = 0.0
in_air = "NULL"
gps_info = "NULL"
latitude_deg = 0.0
longitude_deg = 0.0
absolute_altitude_m = 0.0
relative_altitude_m = 0.0


def takeoffControl():
    global takeoffCommand
    if not takeoffCommand:
        takeoffCommand = True


def landControl():
    global landCommand
    if not landCommand:
        landCommand = True


def missionControl():
    global missionCommand
    if not missionCommand:
        missionCommand = True


def target1Control():
    global target1Command
    if not target1Command:
        target1Command = True


def target2Control():
    global target2Command
    if not target2Command:
        target2Command = True


def target3Control():
    global target3Command
    if not target3Command:
        target3Command = True


def refreshControl():
    global refreshCommand
    if not refreshCommand:
        refreshCommand = True


# 设置侦察任务
scout_mission = [MissionItem(22.58927,
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
                             float('nan')),
                 MissionItem(22.58739,
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
                             float('nan')),
                 MissionItem(22.58680,
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
    # await drone.connect(system_address="serial:///dev/ttyUSB0")
    await drone.connect(system_address="udp://:14540")

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
    global drone, takeoffCommand, landCommand, missionCommand, target1Command, target2Command, target3Command, refreshCommand
    global flightmode, battery, in_air, gps_info, latitude_deg, longitude_deg, absolute_altitude_m, relative_altitude_m

    while True:
        display.fill((255, 255, 255))

        # Show the button
        btn_takeoff.show()
        btn_land.show()
        btn_mission.show()
        btn_target1.show()
        btn_target2.show()
        btn_target3.show()
        btn_refresh.show()

        font = pygame.font.SysFont("Arial", 20, italic=False)

        flightmodetext = font.render(f"Flight Mode:  {flightmode}", True, (0, 0, 0))
        display.blit(flightmodetext, (10, 400))
        batterytext = font.render(f"Battery:  {battery}", True, (0, 0, 0))
        display.blit(batterytext, (460, 400))
        in_airtext = font.render(f"In Air:  {in_air}", True, (0, 0, 0))
        display.blit(in_airtext, (460, 350))
        gps_infotext = font.render(f"GPS Info:  {gps_info}", True, (0, 0, 0))
        display.blit(gps_infotext, (10, 450))
        latitude_degtext = font.render(f"latitude_deg:  {latitude_deg}", True, (0, 0, 0))
        display.blit(latitude_degtext, (10, 500))
        longitude_degtext = font.render(f"longitude_deg:  {longitude_deg}", True, (0, 0, 0))
        display.blit(longitude_degtext, (460, 500))
        absolute_altitude_mtext = font.render(f"absolute_altitude_m:  {absolute_altitude_m}", True, (0, 0, 0))
        display.blit(absolute_altitude_mtext, (10, 550))
        relative_altitude_mtext = font.render(f"relative_altitude_m:  {relative_altitude_m}", True, (0, 0, 0))
        display.blit(relative_altitude_mtext, (460, 550))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        pygame.display.update()

        # keys = pygame.key.get_pressed()

        # While being in air and landing mode the drone is not likely to takeoff again, so
        # a condition check is required here to avoid such a condition.

        if takeoffCommand and (await print_in_air(drone) != True):  # 按 上 起飞
            print("takeoff begin")
            takeoffCommand = False
            await takeoff()
            print("takeoff end")

        elif landCommand:  # 按 下 降落
            print("land begin")
            landCommand = False
            await land()
            print("land end")

        elif missionCommand and (await print_in_air(drone) == True):  # 按 m 进入侦察任务
            print("scout begin")
            missionCommand = False
            await runMission(scout_mission, False)
            print("scout end")

        elif target1Command and (await print_in_air(drone) == True):  # 按 1 前往打击点1
            print("bomb1 begin")
            target1Command = False
            if not await drone.mission.is_mission_finished():
                await drone.mission.pause_mission()
                await drone.mission.clear_mission()
            await runMission(bomb1, True)
            print("bomb1 end")

        elif target2Command and (await print_in_air(drone) == True):  # 按 2 前往打击点2
            print("bomb2 begin")
            target2Command = False
            if not await drone.mission.is_mission_finished():
                await drone.mission.pause_mission()
                await drone.mission.clear_mission()
            await runMission(bomb2, True)
            print("bomb2 end")

        elif target3Command and (await print_in_air(drone) == True):  # 按 3 前往打击点3
            print("bomb3 begin")
            target3Command = False
            if not await drone.mission.is_mission_finished():
                await drone.mission.pause_mission()
                await drone.mission.clear_mission()
            await runMission(bomb3, True)
            print("bomb3 end")

        elif refreshCommand:
            refreshCommand = False
            # asyncio.ensure_future(info(drone))
            # await asyncio.sleep(0.05)
            await info(drone)

        # elif keys[pygame.K_RIGHT]:  # 按 右 打印是否在空中
        #     await print_in_air(drone)

        # elif keys[pygame.K_i]:  # 按 i 打印 电池, 是否在空中, gps, 位置信息
        #     await info(drone)

        # elif keys[pygame.K_r]:  # 按r打印以度为单位的侧倾角，正值向右倾斜
        #     await print_roll_deg(drone)

        # elif keys[pygame.K_a]:  # arm
        #     await drone.action.arm()

        # else:
            # asyncio.ensure_future(info(drone))
            # await asyncio.sleep(0.05)
            # await info(drone)


async def print_flightmode(drone):
    async for flight_mode in drone.telemetry.flight_mode():
        print("FlightMode:", flight_mode)
        return flight_mode


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
    global flightmode, battery, in_air, gps_info, latitude_deg, longitude_deg, absolute_altitude_m, relative_altitude_m

    battery = await print_battery(drone)
    in_air = await print_in_air(drone)
    gps_info = await print_gps_info(drone)
    position = await print_position(drone)
    latitude_deg = position.latitude_deg
    longitude_deg = position.longitude_deg
    absolute_altitude_m = position.absolute_altitude_m
    relative_altitude_m = position.relative_altitude_m
    flightmode = await print_flightmode(drone)

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


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup())
    loop.run_until_complete(main())
