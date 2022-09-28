import cv2
import numpy as np

def positiveNum(num):
    res = num
    if(num < 0):
        res = 0
    return res

def findRectangle(contours):
    for cnt in contours:
        # 最小外界矩形的宽度和高度
        width, height = cv2.minAreaRect(cnt)[1]
        if width* height > 100:
            # 最小的外接矩形
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)  # 获取最小外接矩形的4个顶点
            box = np.int0(box)
            
            if 0 not in box.ravel():
                return rect

def cv_filter2d(img_path):
    src = cv2.imread(img_path)

    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])

    dst = cv2.filter2D(src, -1, kernel)

    cv2.imshow('original', src)

    cv2.imshow('dst', dst)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

#read the image
def identify(img, i):
    #convert the BGR image to HSV colour space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    #obtain the grayscale image of the original image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #set the bounds for the red hue
    lower_red = np.array([156,43,46])
    upper_red = np.array([180,255,255])

    #create a mask using the bounds set
    mask = cv2.inRange(hsv, lower_red, upper_red)
    #create an inverse of the mask
    mask_inv = cv2.bitwise_not(mask)
    # cv2.imwrite('mask_inv.png', mask_inv)
    contours, _ = cv2.findContours(mask_inv, 2, 2)

    angle = 0.0
    center = (0, 0)
    long = 0
    short = 0
    for cnt in contours:
        # 最小外界矩形的宽度和高度
        width, height = cv2.minAreaRect(cnt)[1]

        if width* height > 100:
            # 最小的外接矩形
            rect = cv2.minAreaRect(cnt)
            center = rect[0]
            box = cv2.boxPoints(rect)  # 获取最小外接矩形的4个顶点
            box = np.int0(box)
            
            if 0 not in box.ravel():
                # 绘制最小外接矩形
                # for i in range(4):
                #     cv2.line(img, tuple(box[i]), tuple(box[(i+1)%4]), 0)  # 5
                # cv2.imshow('img', img)
                # cv2.waitKey()
                theta = cv2.minAreaRect(cnt)[2]
                # print('thete = ', theta)
                # if abs(theta) <= 45:
                #     print('图片的旋转角度为%s.'%theta)
                angle = theta
                long = height
                short = width
                if(height < width):
                    long = width
                    short = height
                    angle = theta - 90

    # 仿射变换,对图片旋转angle角度
    h, w = mask_inv.shape
    # print('h = ', h , 'w = ', w)
    # center = (w//2, h//2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    mask_rotated = cv2.warpAffine(mask, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    # cv2.imwrite('after_rotated.png', rotated)
    # print(int(center[1]-long/2), int(center[1]+long/2), int(center[0]-short/2), int(center[0]+short/2))
    cutted_rgb_img = rotated[positiveNum(int(center[1]-long/2)):positiveNum(int(center[1]+long/2)), positiveNum(int(center[0]-short/2)):positiveNum(int(center[0]+short/2))]
    cv2.imwrite('out/'+str(i)+'cutted_rgb_img.png', cutted_rgb_img)
    cutted_mask = mask_rotated[positiveNum(int(center[1]-long/2)):positiveNum(int(center[1]+long/2)), positiveNum(int(center[0]-short/2)):positiveNum(int(center[0]+short/2))]
    # if(np.max(cutted_mask) is None):
    #     return
    if(cutted_mask.size == 0):
        return
    dilate=cv2.dilate(cutted_mask, None, iterations=1)
    contours, _ = cv2.findContours(dilate, 2, 2)
    rect = findRectangle(contours)
    if(cutted_rgb_img.size == 0 or cutted_rgb_img is None):
        return
    number_rgb_img = cutted_rgb_img[positiveNum(int(rect[0][1]-rect[1][1]/2)):positiveNum(int(rect[0][1]+rect[1][1]/2)), positiveNum(int(rect[0][0]-rect[1][0]/2)):positiveNum(int(rect[0][0]+rect[1][0]/2))]
    cv2.imwrite('out/'+str(i)+'number_rgb_img.png', number_rgb_img)
    kernel = np.array([[0, -1, 0],
                        [-1, 5, -1],
                        [0, -1, 0]])

    sharped_number_rgb = cv2.filter2D(number_rgb_img, -1, kernel)
    cv2.imwrite('out/'+str(i)+'sharped_number_rgb.png', sharped_number_rgb)
    bin_number_img = cv2.adaptiveThreshold(cv2.cvtColor(sharped_number_rgb, cv2.COLOR_BGR2GRAY), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 5)
    cv2.imwrite('out/'+str(i)+'bin_number_img.png', bin_number_img)
    # cv2.imshow('cutted_rgb_img', cutted_rgb_img)
    # cv2.imshow('number_rgb_img.png', number_rgb_img)
    # cv2.imshow('sharped_number_rgb.png', sharped_number_rgb)
    # cv2.imshow('fbin_number_img.png', bin_number_img)
    # cv2.waitKey()


