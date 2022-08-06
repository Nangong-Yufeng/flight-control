"""控制逻辑（吧）"""
from mavsdk import System
from mavsdk.mission import MissionItem
from logOutput import log_info
import asyncio

drone = System()  # 无人机实例

# 设置侦察任务
scout_missions = [MissionItem(22.58927,
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
                     10, True,
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


async def setup(callback):
    """
    General configurations, setups, and connections are done here.
    :return:
    """
    global drone  # 上面的无人机实例
    # todo:这另一个是啥？
    # await drone.connect(system_address="serial:///dev/ttyUSB0")
    await drone.connect(system_address="udp://:14540")
    log_info("Waiting for drone to connect...")
