# import cv2

# img = cv2.imread('img/test.png')
# # 转为灰度图
# new_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# height, width = new_img.shape[0:2]

# # 设置阈值
# thresh = 60

# # 遍历每一个像素点
# for row in range(height):
#     for col in range(width):
#         # 获取到灰度值
#         gray = new_img[row, col]
#         # 如果灰度值高于阈值 就等于255最大值
#         if gray > thresh:
#             new_img[row, col] = 255
#         # 如果小于阈值，就直接改为0
#         elif gray < thresh:
#             new_img[row, col] = 0

# cv2.imshow('img', new_img)
# cv2.waitKey()
import cv2

img = cv2.imread('img/test.png', cv2.IMREAD_GRAYSCALE)
i = 0
j = 0
k = 0
l = 0
m = 0
for i in range(3, 10):
    if(i % 2 == 1):
        for j in range(3, 10):
            if(j % 2 == 1):
                for k in range(1, 5):
                    # if(k % 2 == 1):
                    gaussian_img = cv2.GaussianBlur(img, (i, j), k)
                    for l in range(3, 8):
                        if(l % 2 == 1):
                            for m in range(1, 5):
                                thresh_img2 = cv2.adaptiveThreshold(gaussian_img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, l, m)
                                cv2.imwrite('output/'+str(i)+str(j)+str(k)+str(l)+str(m)+'.png', thresh_img2)
# 使用高斯滤波模糊图像  参数1： 图片矩阵  参数2：卷积核 参数3： 越大越模糊
# gaussian_img = cv2.GaussianBlur(img, (3, 5), 0)
# cv2.imshow('gaussian_img', gaussian_img)
# thresh_img1 = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 3, 2)
# thresh_img2 = cv2.adaptiveThreshold(gaussian_img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 3, 2)

# cv2.imshow('thresh_img1', thresh_img1)
# cv2.imshow('thresh_img2', thresh_img2)
# cv2.waitKey()
# import cv2

# img = cv2.imread('img/test.png', cv2.IMREAD_GRAYSCALE)

# # 使用255的阈值进行二值化
# # ret, thresh_img = cv2.threshold(img, 255, 255, cv2.THRESH_BINARY)
# # cv2.imshow('normal', thresh_img)

# # 使用高斯滤波模糊图像  参数1： 图片矩阵  参数2：卷积核 参数3： 越大越模糊
# # gaussian_img = cv2.GaussianBlur(img, (3, 3), 0)
# # cv2.imshow('gaussian_img', gaussian_img)

# # 使用大津算法0阈值二值化经过高斯滤波模糊后的图像
# # ret, thresh_img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

# # cv2.imshow('otsu', thresh_img)

# cv2.imshow('img', img) #目前来看效果不错
# cv2.waitKey()
