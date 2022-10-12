#!/usr/bin/env python3

import asyncio

from mavsdk import System
from mavsdk.mission import (MissionItem, MissionPlan)

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

async def run():
    detect_flag = True
    i = 1
    drone = System()
    # await drone.connect(system_address="udp://:14540")
    await drone.connect(system_address="serial:///dev/ttyUSB0") # Ubuntu在tty*端口连接

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone discovered!")
            break
    
    while detect_flag:
        print_mission_progress_task = asyncio.ensure_future(
            print_mission_progress(drone, i))

        running_tasks = [print_mission_progress_task]
        termination_task = asyncio.ensure_future(
            observe_is_in_air(drone, running_tasks))

        waypoint_lists = [
            [22.5917867, 113.9752335, 80, 13, 3],
            [22.5915777, 113.9755941, 80, 13, 3],
            [22.5912497, 113.9752591, 80, 13, 3],
            [22.5909264, 113.9752896, 80, 13, 1],
            [22.5904671, 113.9752947, 80, 13, 1],
            [22.5899377, 113.9753048, 80, 13, 1],
            [22.5896097, 113.9753099, 80, 13, 3],
            [22.5892395, 113.9757920, 80, 13, 3],
            [22.5888647, 113.9753353, 80, 13, 3],
            [22.5892067, 113.9749699, 80, 13, 3],
            [22.5896097, 113.9753099, 80, 13, 3],
            [22.5899377, 113.9753048, 80, 13, 1],
            [22.5904671, 113.9752947, 80, 13, 1],
            [22.5909264, 113.9752896, 80, 13, 1],
            [22.5912497, 113.9752591, 80, 13, 3],
            [22.5915214, 113.9748887, 80, 13, 3]
        ]
        mission_items = generate_mission(waypoint_lists)

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
        # if mission_progress.current == 3:
        #     await drone.mission.pause_mission()
        #     print("--Mission has been paused !")
        #     return 


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
        # print(f"Mission progress: "
        #       f"{mission_progress.current}/"
        #       f"{mission_progress.total}")
        # if mission_progress.current == 3:
            # await drone.mission.pause_mission()
            # print("--Mission has been paused !")
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
    loop.run_until_complete(run())
