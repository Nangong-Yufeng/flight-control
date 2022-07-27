import cv2
import numpy as np
 
 
xs,ys,ws,hs = 0,0,0,0  #selection.x selection.y
xo,yo=0,0 #origin.x origin.y
selectObject = False
trackObject = 0
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
 
cap = cv2.VideoCapture(0)  # 摄像头输入
# ret判断是否读到图片
# frame读取到的当前帧的矩阵
# 返回的是元组类型，所以也可以加括号
ret,frame = cap.read()
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
        dst = cv2.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)
        dst &= mask
        ret, track_window = cv2.CamShift(dst, track_window, term_crit)
        pts = cv2.boxPoints(ret)
        pts = np.int0(pts)
        img2 = cv2.polylines(frame,[pts],True, 255,2)
        
    if selectObject == True and ws>0 and hs>0:
        cv2.imshow('imshow1',frame[ys:ys+hs,xs:xs+ws])
        cv2.bitwise_not(frame[ys:ys+hs,xs:xs+ws],frame[ys:ys+hs,xs:xs+ws])
    cv2.imshow('imshow',frame)
    if  cv2.waitKey(10)==27:  # 等待10s，按ESC退出
        break
cv2.destroyAllWindows()