import cv2
import numpy as np

# Load image, grayscale, bilaterial filter, Otsu's threshold
image = cv2.imread('img/test02.png')
original = image.copy()
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blur = cv2.bilateralFilter(gray,9,75,75)
thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

# Find contours, perform contour approximation, and extract ROI
ROI_num = 0
cnts = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]
for c in cnts:
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.04 * peri, True)
    # If has 5 then its a pentagon
    if len(approx) == 5:
        x,y,w,h = cv2.boundingRect(approx)
        cv2.rectangle(image, (x, y), (x + w, y + h), (200,255,12), 2)
        ROI = original[y:y+h, x:x+w]
        cv2.imwrite('ROI_{}.png'.format(ROI_num), ROI)
        ROI_num += 1

cv2.imshow('thresh', thresh)
cv2.imshow('ROI', ROI)
cv2.imshow('image', image)
cv2.waitKey()