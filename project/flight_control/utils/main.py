from flight_control.utils.logOutput import log_info
import pygame
import display as dp  # 用于显示UI操作界面
import control

drone = control.drone  # control那边创建的一个System实例

buttons = dp.getButtons()  # 获得一堆按钮

init_info = pygame.init()
log_info("init:" + str(init_info))  # 初始化并将初始化后的消息打印出来

while True:
    # 关于显示
    dp.check_for_quit()  # 能用右上角红叉叉关闭
    dp.display.fill((196, 196, 196))  # 背景上色
    for button in buttons:  # 显示按钮
        button.show()
    pygame.display.update()  # 刷新
