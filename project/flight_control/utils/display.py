"""
显示模块，负责UI界面的绘制（可能吧）
"""

import pygame
from flight_control.ui_elements import button
from logOutput import log_info
import pyperclip


WIDTH = 900  # 界面宽
HEIGHT = 600  # 界面高
# FPS = ?
TITLE = "a title"  # 界面标题
BUTTON_COLOR = (128, 128, 128)  # 按钮颜色

display = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)

takeoffCommand = False
landCommand = False
missionCommand = False
target1Command = False
target2Command = False
target3Command = False
refreshCommand = False
bombCommand = False
armCommand = False


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

def bombControl():
    global bombCommand
    while True:
        data = pyperclip.paste()
        # print(data)
        if(data == 'bomb'):
            bombCommand = True
            break
    # if not bombCommand:
    #     bombCommand = True

def armControl():
    global armCommand
    if not armCommand:
        armCommand = True


def getButtons():
    btn_takeoff = button.button(display, BUTTON_COLOR,
                                "Takeoff",
                                (25, 25, 150, 50),
                                lambda: takeoffControl(),
                                border_radius=5, font_family="Arial", font_size=18)

    btn_land = button.button(display, BUTTON_COLOR,
                             "Land",
                             (225, 25, 150, 50),
                             lambda: landControl(),
                             border_radius=5, font_family="Arial", font_size=18)

    btn_mission = button.button(display, BUTTON_COLOR,
                                "Scout Mission",
                                (25, 125, 350, 50),
                                lambda: missionControl(),
                                border_radius=5, font_family="Arial", font_size=18)

    btn_target1 = button.button(display, BUTTON_COLOR,
                                "Target 1",
                                (25, 225, 100, 50),
                                lambda: target1Control(),
                                border_radius=5, font_family="Arial", font_size=18)

    btn_target2 = button.button(display, BUTTON_COLOR,
                                "Target 2",
                                (150, 225, 100, 50),
                                lambda: target2Control(),
                                border_radius=5, font_family="Arial", font_size=18)

    btn_target3 = button.button(display, BUTTON_COLOR,
                                "Target 3",
                                (275, 225, 100, 50),
                                lambda: target3Control(),
                                border_radius=5, font_family="Arial", font_size=18)

    btn_refresh = button.button(display, BUTTON_COLOR,
                                "Refresh Info",
                                (25, 325, 350, 50),
                                lambda: refreshControl(),
                                border_radius=5, font_family="Arial", font_size=18)

    btn_bomb = button.button(display, (0, 255, 0),
                             "BOMB MOD",
                             (525, 25, 150, 50),
                             lambda: bombControl(),
                             border_radius=5, font_family="Arial", font_size=18)

    btn_arm = button.button(display, (0, 255, 0),
                            "Arm",
                            (725, 25, 150, 50),
                            lambda: armControl(),
                            border_radius=5, font_family="Arial", font_size=18)

    return [btn_takeoff, btn_land, btn_mission, btn_target1, btn_target2, btn_target3, btn_refresh, btn_bomb, btn_arm]


def check_for_quit():
    """
    右上角叉叉关闭功能
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()


if __name__ == '__main__':
    print("==========================")
    init_info = pygame.init()
    log_info("init:" + str(init_info))
    buttons = getButtons()
    while True:
        display.fill((196, 196, 196))
        for button in buttons:
            button.show()
        check_for_quit()
        pygame.display.update()
