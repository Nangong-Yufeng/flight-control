import cv2

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

cv2.namedWindow('imshow', 0)
cv2.resizeWindow('imshow', 1920, 1080)

while True:
    ret, frame = cap.read()
    cv2.imshow('imshow', frame)

    if  cv2.waitKey(10)==27:  # 等待10s，按ESC退出
        break

cv2.destroyAllWindows()
