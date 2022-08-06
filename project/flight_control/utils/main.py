from flight_control.utils.logOutput import log_info
import pygame
import display as dp  # 用于显示UI操作界面
import control

drone = control.drone

buttons = dp.getButtons()
init_info = pygame.init()
log_info("init:" + str(init_info))

while True:
    # 关于显示
    dp.check_for_quit()  # 能用右上角红叉叉关闭
    dp.display.fill((196, 196, 196))
    for button in buttons:
        button.show()
    pygame.display.update()