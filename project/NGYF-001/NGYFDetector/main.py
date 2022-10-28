from utils import NGYFDetector
import cv2 as cv

image = cv.imread('../assets/image1.png')
image2 = cv.imread('../assets/image2.png')
image3 = cv.imread('../assets/image3.png')
detector = NGYFDetector()
x, y = detector.detect(image)
print(x, y)
x, y = detector.detect(image2)
print(x, y)
x, y = detector.detect(image3)
print(x, y)
