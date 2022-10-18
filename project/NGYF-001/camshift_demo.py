from math import fabs
import cv2
import numpy as np
import os
import threading
import asyncio
from mavsdk import System
import nest_asyncio

nest_asyncio.apply()

init_mavsdk_server = r'"sources\mavsdk-windows-x64-release\bin\mavsdk_server_bin.exe -p 50051 serial://COM4:57600"' # 你要运行的exe文件
drone = System(mavsdk_server_address='localhost', port=50051)


xs,ys,ws,hs = 0,0,0,0  #selection.x selection.y
xo,yo=0,0 #origin.x origin.y
selectObject = False
trackObject = 0
gimbal_servo = 0.0


def open_mavsdk_server():
        server = os.system(init_mavsdk_server)
        print (server)


def connect_plane(loop, drone):
    print('连接飞机中···')
    loop.run_until_complete(drone_connect(drone))


async def drone_connect(drone:System):
    # await drone.connect(system_address="udp://:14540")
    await drone.connect()
    print('飞机连接成功！')


def onMouse(event, x, y, flags, prams):  # 设置跟踪框参数
    global xs,ys,ws,hs,selectObject,xo,yo,trackObject
    if selectObject == True:
        xs = min(x, xo)
        ys = min(y, yo)
        
        ws = abs(x-xo)
        hs = abs(y-yo)
    if event == cv2.EVENT_LBUTTONDOWN:
        xo,yo = x, y
        xs,ys,ws,hs= x, y, 0, 0
        selectObject = True
    elif event == cv2.EVENT_LBUTTONUP:
        selectObject = False
        trackObject = -1


def set_actuator_thread(loop, drone, add):
    global gimbal_servo
    loop.run_until_complete(set_actuator_drone(drone, gimbal_servo+add))
    gimbal_servo += add


async def set_actuator_drone(drone:System, gimbal_servo):
    # await drone.action.arm()
    await drone.action.set_actuator(1, gimbal_servo)
    await asyncio.sleep(0.2)
    

loop = asyncio.get_event_loop()
mavsdk_thread = threading.Thread(target=open_mavsdk_server).start()
connect_plane_thread = threading.Thread(target=connect_plane, args=(loop, drone))
connect_plane_thread.start()
connect_plane_thread.join()
threading.Thread(target=set_actuator_thread, args=(loop, drone, 0)).start()
cap = cv2.VideoCapture(0)  # 摄像头输入
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# ret判断是否读到图片
# frame读取到的当前帧的矩阵
# 返回的是元组类型，所以也可以加括号
ret,frame = cap.read()
print(frame.shape)
cv2.namedWindow('imshow')
cv2.setMouseCallback('imshow',onMouse)
term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )  # 设置迭代的终止标准，最多十次迭代
while(True):
    ret,frame = cap.read()
    # print("frame = ", frame)
    # print("==========================================")
    if trackObject != 0:
        hsv =  cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # RGB转为HSV更好处理
        # inRange函数设置亮度阈值
        # 去除低亮度的像素点的影响
        # eg. mask = cv2.inRange(hsv, lower_red, upper_red)
        mask = cv2.inRange(hsv, np.array((0., 30.,10.)), np.array((180.,256.,255.)))
        # print('trackObject = ', trackObject)
        if trackObject == -1:
            
            track_window=(xs,ys,ws,hs)  # 设置跟踪框参数
            maskroi = mask[ys:ys+hs, xs:xs+ws]
            hsv_roi = hsv[ys:ys+hs, xs:xs+ws]
            # 然后得到框中图像的直方图
            # cv2.calcHist(images, channels, mask, histSize, ranges[, hist[, accumulate ]])
            # mask 即上文的阈值设置
            # histSize表示这个直方图分成多少份（即多少个直方柱）
            # range是表示直方图能表示像素值的范围
            # 返回直方图


            # 反向投影函数（特征提取函数）
            # 反向投影是一种记录给定图像中的像素点如何适应直方图模型像素分布的方式
            # 反向投影就是首先计算某一特征的直方图模型，然后使用模型去寻找图像中存在的特征
            # cv2.calcHist(images, channels, mask, histSize, ranges[, hist[, accumulate]])

            # images:待处理的图像，图像格式为uint8或float32
            # channels:对应图像需要统计的通道，若是灰度图则为0，彩色图像B、G、R对应0、1、2
            # mask:掩膜图像。如果统计整幅图像就设置为None，否则这里传入设计的掩膜图像。
            # histSize表示这个直方图分成多少份（即多少个直方柱）
            # ranges:像素量化范围，通常为0 - 255。
            roi_hist = cv2.calcHist([hsv_roi],[0],maskroi,[180],[0,180])

            # 归一化函数cv2.normalize(src[, dst[, alpha[, beta[, norm_type[, dtype[, mask]]]]]])
            # 返回dst类型
            # 归一化就是要把需要处理的数据经过处理后（通过某种算法）限制在你需要的一定范围内
            # src  - 输入数组
            # dst  - 与src大小相同的输出数组
            # alpha  - 范围值，   以便在范围归一化的情况下归一化到较低范围边界
            # beta  - 范围归一化时的上限范围; 它不用于标准规范化
            # normType  - 规范化类型 这里的NORM_MINMAX是数组的数值被平移或缩放到一个指定的范围，线性归一化。
            # dtype  - 当为负数时，输出数组与src的类型相同；否则，它具有与src相同的通道数；深度=CV_MAT_DEPTH（dtype）
            # mask  - 可选的操作掩码。
            cv2.normalize(roi_hist,roi_hist,0,255,cv2.NORM_MINMAX)
            trackObject = 1
        # print('roi_hist = ', roi_hist)
        dst = cv2.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)
        dst &= mask
        ret, track_window = cv2.CamShift(dst, track_window, term_crit)
        pts = cv2.boxPoints(ret)
        pts = np.int0(pts)
        target_x = (pts[0][0]+pts[1][0]+pts[2][0]+pts[3][0]) / 4
        target_y = (pts[0][1]+pts[1][1]+pts[2][1]+pts[3][1]) / 4
        if(fabs(target_y - 540) > 100):
            if(540-target_y > 0):
                g_thread = threading.Thread(target=set_actuator_thread, args=(loop, drone, 0.1))
                g_thread.start()
                g_thread.join()
            if(540-target_y < 0):
                g_thread = threading.Thread(target=set_actuator_thread, args=(loop, drone, -0.1))
                g_thread.start()
                g_thread.join()
        img2 = cv2.polylines(frame,[pts],True, 255,2)
        
    if selectObject == True and ws>0 and hs>0:
        cv2.imshow('imshow1',frame[ys:ys+hs,xs:xs+ws])
        cv2.bitwise_not(frame[ys:ys+hs,xs:xs+ws],frame[ys:ys+hs,xs:xs+ws])
    cv2.imshow('imshow',frame)
    if  cv2.waitKey(10)==27:  # 等待10s，按ESC退出
        break
cv2.destroyAllWindows()