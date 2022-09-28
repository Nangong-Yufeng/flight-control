import cv2

img = cv2.imread('11frame.png')
img_cut = img[2:131, 398:480] #!!!!!居然第一个参数是y第二个参数是x
cv2.imshow('cutted!', img_cut)
cv2.waitKey()