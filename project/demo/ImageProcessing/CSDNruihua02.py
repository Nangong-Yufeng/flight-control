#导入库
import cv2
import numpy as np
#导入图片
img=cv2.imread("final_img.png")
#转换灰度
gimg=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#拉普拉斯算子锐化
kernel=np.array([[0,-1,0],[-1,5,-1],[0,-1,0]],np.float32)#定义拉普拉斯算子
dst=cv2.filter2D(img,-1,kernel=kernel)#调用opencv图像锐化函数
#sobel算子锐化
#对x方向梯度进行sobel边缘提取
x=cv2.Sobel(gimg,cv2.CV_64F,1,0)
#对y方向梯度进行sobel边缘提取
y=cv2.Sobel(gimg,cv2.CV_64F,0,1)
#对x方向转回uint8
absX=cv2.convertScaleAbs(x)
#对y方向转会uint8
absY=cv2.convertScaleAbs(y)
#x，y方向合成边缘检测结果
dst1=cv2.addWeighted(absX,0.5,absY,0.5,0)
#与原图像堆叠
res=dst1+gimg
#测试
#print("dstshape:",dst1)
#print("resshape:",res)
#按要求左右显示原图与拉普拉斯处理结果
imges1=np.hstack([img,dst])
cv2.imshow('lapres',imges1)
#按要求左右显示原图与sobel处理结果
image=np.hstack([gimg,res])
cv2.imshow('sobelres',image)
#去缓存
cv2.waitKey(0)
cv2.destroyAllWindows()