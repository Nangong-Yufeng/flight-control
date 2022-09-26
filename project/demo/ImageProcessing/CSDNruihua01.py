import cv2 as cv
import numpy as np

def cv_filter2d(img_path):
    src = cv.imread(img_path)

    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])

    dst = cv.filter2D(src, -1, kernel)

    cv.imshow('original', src)

    cv.imshow('dst', dst)

    cv.waitKey(0)
    cv.destroyAllWindows()

img_path = r"final_img.png"
cv_filter2d(img_path)
