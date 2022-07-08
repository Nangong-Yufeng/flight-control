#!/usr/bin/env python3

import asyncio
import pygame
import numpy as np

from mavsdk import System
from mavsdk.mission import *

pygame.init()
window = pygame.display.set_mode((300, 300))

drone = System()
pos = [[22.58927, 113.96436], [22.58739, 113.96771], [22.58680, 113.96645]]
pos = np.array(pos)
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
                             float('nan')), MissionItem(22.58739,
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
                                                        float('nan')), MissionItem(22.58680,
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


async def setup():
    """
    General configurations, setups, and connections are done here.
    :return:
    """
    global drone
    await drone.connect(system_address="udp://:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"Drone discovered!")
            break

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok:
            print("Global position estimate ok")
            break


async def main():
    global drone
    running = True

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # While being in air and landing mode the drone is not likely to takeoff again, so
        # a condition check is required here to avoid such a condition.

        if keys[pygame.K_UP] and (await print_in_air(drone) != True):
            await takeoff()

        elif keys[pygame.K_DOWN]:
            await land()

        elif keys[pygame.K_m] and (await print_in_air(drone) == True):
            await runMission(scout_mission, False)

        elif keys[pygame.K_g] and keys[pygame.K_1] and (await print_in_air(drone) == True):
            if not await drone.mission.is_mission_finished():
                await drone.mission.pause_mission()
            await runMission(bomb1, True)

        elif keys[pygame.K_g] and keys[pygame.K_2] and (await print_in_air(drone) == True):
            if not await drone.mission.is_mission_finished():
                await drone.mission.clear_mission()
            await runMission(bomb2, True)

        elif keys[pygame.K_g] and keys[pygame.K_3] and (await print_in_air(drone) == True):
            if not await drone.mission.is_mission_finished():
                await drone.mission.clear_mission()
            await runMission(bomb3, True)

        elif keys[pygame.K_RIGHT]:
            await print_in_air(drone)

        elif keys[pygame.K_i]:
            await info(drone)


async def goto(target):  # it's useless
    global drone
    if not await drone.mission.is_mission_finished():
        await drone.mission.pause_mission()
    print("Going to", end=" ")
    print(target)
    await drone.action.goto_location(target[0], target[1], 50, 0)


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

    print_mission_progress_task = asyncio.ensure_future(
        print_mission_progress(drone))

    running_tasks = [print_mission_progress_task]
    termination_task = asyncio.ensure_future(
        observe_is_in_air(drone, running_tasks))

    mission_plan = MissionPlan(mission_items)

    await drone.mission.set_return_to_launch_after_mission(is_back)

    print("-- Uploading mission")
    await drone.mission.upload_mission(mission_plan)

    print("-- Arming")
    await drone.action.arm()

    print("-- Starting mission")
    await drone.mission.start_mission()

    await termination_task


async def print_mission_progress(drone):
    async for mission_progress in drone.mission.mission_progress():
        print(f"Mission progress: "
              f"{mission_progress.current}/"
              f"{mission_progress.total}")
        await info(drone)


async def observe_is_in_air(drone, running_tasks):
    """ Monitors whether the drone is flying or not and
    returns after landing """

    was_in_air = False

    async for is_in_air in drone.telemetry.in_air():
        if is_in_air:
            was_in_air = is_in_air

        if was_in_air and not is_in_air:
            for task in running_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            await asyncio.get_event_loop().shutdown_asyncgens()

            return


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup())
    loop.run_until_complete(main())
