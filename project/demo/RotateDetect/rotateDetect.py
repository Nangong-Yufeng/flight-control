import cv2

imagepath = 'test.png'
img = cv2.imread(imagepath, 1)

# 将图片的边缘变为白色
height, width = img.shape[0:2]
for i in range(width):
    img[0, i] = [255]*3
    img[height-1, i] = [255]*3
for j in range(height):
    img[j, 0] = [255]*3
    img[j, width-1] = [255]*3

# 去掉灰色线（即噪声）
for i in range(height):
    for j in range(width):
        if list(img[i,j]) == [204,213,204]:
            img[i,j]=[255]*3

# 把图片转换为灰度模式
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# 中值滤波
blur = cv2.medianBlur(gray, 1)  # 模板大小3*3
# 二值化
ret,thresh = cv2.threshold(blur, 200, 255, cv2.THRESH_BINARY)
# 保存图片
cv2.imwrite('testout.png', thresh)
