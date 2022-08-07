from calendar import c
from pathlib import Path
from re import T
from turtle import pos
from xml.etree.ElementTree import ProcessingInstruction
import cv2
import numpy as np
from numpy import fabs
import torch
import torch.backends.cudnn as cudnn
import time
import threading
import win32clipboard as wc
import win32con
from models.experimental import attempt_load
from utils.datasets import LoadStreams
from utils.general import check_img_size, check_suffix, non_max_suppression, scale_coords, xyxy2xywh
from utils.plots import Annotator
from utils.torch_utils import select_device


#@torch.no_grad()
device = select_device('')
# device = torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")
half = True
# half = device.type != 'cpu'
weights = 'best.pt'
#模型尺寸
imgsz = 640

show_default_results = True#是否观看默认结果

src = '1'  # 从摄像头读取视频输入

pos_x = 320
pos_y = 240


#置信度 阈值
conf_thres=0.3
iou_thres=0.2
classes=None
agnostic_nms=False
#这个考虑降低   默认1000
max_det=1000  
plus_x = 25
plus_y = 18.75
line_thickness = 2
save_conf = False
hide_labels = False
hide_conf = False
w = str(weights[0] if isinstance(weights, list) else weights)
classify, suffix, suffixes = False, Path(w).suffix.lower(), ['.pt', '.onnx', '.tflite', '.pb', '']
check_suffix(w, suffixes)
pt, onnx, tflite, pb, saved_model = (suffix == x for x in suffixes)
model = torch.jit.load(w) if 'torchscript' in w else attempt_load(weights, map_location=device)
stride = int(model.stride.max()) 
names = model.module.names if hasattr(model, 'module') else model.names  # get class names

model.half()
imgsz = check_img_size(imgsz, s=stride)
model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters()))) 


# =====Camshift Part=====
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
 
cv2.namedWindow('RANX_AI')
cv2.setMouseCallback('RANX_AI',onMouse)
term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )  # 设置迭代的终止标准，最多十次迭代
# =====Camshift Part=====


def bomb_func():
    aString = 'bomb'
    wc.OpenClipboard()
    wc.EmptyClipboard()
    wc.SetClipboardData(win32con.CF_TEXT, aString.encode('GBK')) # 解决中文乱码
    # wc.CloseClipboard()


def startdetect():
    global trackObject
    if show_default_results:
        seen = 0
    source = str(src)
    webcam = source.isnumeric() or source.endswith('.txt') or source.lower().startswith(
        ('rtsp://', 'rtmp://', 'http://', 'https://'))
    cudnn.benchmark = True  # set True to speed up constant image size inference
    dataset = LoadStreams(source, img_size=imgsz, stride=stride, auto=pt)
    bs = len(dataset)  # batch_size
    for path, img, im0s, vid_cap in dataset:
        # print("img = ", img)
        # print("======================================================")
        # print("im0s = ", im0s)
        t0 = time.time()
        img = torch.from_numpy(img).to(device)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img = img / 255.0  # 0 - 255 to 0.0 - 1.0
        if len(img.shape) == 3:
            img = img[None]  # expand for batch dim
        pred = model(img, augment=False, visualize=False)[0]
        # NMS
        pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
        t1 = time.time()
        for i, det in enumerate(pred):  # per image
            if show_default_results:
                seen += 1
            s = ''
            s += '%gx%g ' % img.shape[2:]
            img0 = im0s[i].copy()
            frame = im0s[i].copy()
            # print("img0 = ", img0)
            annotator = Annotator(img0, line_width=line_thickness, example=str(names))
            #find:
            img_object = []
            cls_object = []
            if len(det):
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], img0.shape).round()
                # Print results
                for *xyxy, conf, cls in reversed(det):
                    xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) ).view(-1).tolist()
                    cls = int(cls)
                    label = None if hide_labels else (names[cls] if hide_conf else f'{names[cls]} {conf:.2f}')
                    img_object.append(xywh)
                    cls_object.append(names[cls])
                    if show_default_results:
                        annotator.box_label(xyxy, label=label, color=(255, 182, 193))#目标框
                # print(cls_object)
                disttotal = []
                flag = False
                # count = 0
                bombthread_yolo = threading.Thread(target=bomb_func)
                if ((len(img_object) > 0) & ('red' in cls_object)):  # 如果检测到目标
                    # print(cls_object[0],img_object[0][0], img_object[0][1], img_object[0][2], img_object[0][3])bomb
                    for i in range(len(img_object)):
                        distx = fabs(img_object[i][0]-pos_x)
                        disty = fabs(img_object[i][1]-pos_y)
                        if (distx**2 + disty**2) <= 625:  # 如果目标在以中心为圆心，25像素为半径的圆
                            # count = i
                            flag = True
                            print("Bomb YoloV5", end=': ')
                            print(cls_object[i],img_object[i][0], img_object[i][1], img_object[i][2], img_object[i][3])
                            bombthread_yolo.start()
                            bombthread_yolo.join()
                            break
                    # xywh = img_object[count]
                
                # if('q' in cls_object & flag): 
                #     if(img)
                    # distvalue = (float(img_object[0][0]) - pos_x) ** 2 + (float(img_object[0][1]) - pos_y) ** 2
                    # for i in range(len(img_object)):
                    #     dist = (img_object[i][0] - pos_x) ** 2 + (img_object[i][1] - pos_y) ** 2
                    #     disttotal.append(dist)
                    #     if dist < distvalue:
                    #         distvalue = dist
                    #         count = i
                # xywh = img_object[count]
                

            # if show_default_results:
            #     im0 = annotator.result()
            if show_default_results:
                frame = annotator.result()

            # if show_default_results:  # 窗口的fps可用于评估性能
            #     im0 = annotator.result()
            #     fps = 1/(t1-t0)
            #     cv2.putText(im0,':{0}'.format(float('%.1f'%fps)),(0,50),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            #     cv2.circle(im0, (pos_x, pos_y), 25, (255, 0, 0), 2)

            # if show_default_results:
            #     cv2.imshow('RANX_AI', im0)

            # Camshift Part
            if trackObject != 0:
                hsv =  cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # RGB转为HSV更好处理
                mask = cv2.inRange(hsv, np.array((0., 30.,10.)), np.array((180.,256.,255.)))
                if trackObject == -1:
                    track_window=(xs,ys,ws,hs)  # 设置跟踪框参数
                    maskroi = mask[ys:ys+hs, xs:xs+ws]
                    hsv_roi = hsv[ys:ys+hs, xs:xs+ws]
                    roi_hist = cv2.calcHist([hsv_roi],[0],maskroi,[180],[0,180])

                    cv2.normalize(roi_hist,roi_hist,0,255,cv2.NORM_MINMAX)
                    trackObject = 1
                dst = cv2.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)
                dst &= mask
                ret, track_window = cv2.CamShift(dst, track_window, term_crit)
                pts = cv2.boxPoints(ret)
                pts = np.int0(pts)
                # print("pts = ", pts)
                target_x = (pts[0][0]+pts[1][0]+pts[2][0]+pts[3][0]) / 4
                target_y = (pts[0][1]+pts[1][1]+pts[2][1]+pts[3][1]) / 4
                distx_cs = fabs(target_x-pos_x)
                disty_cs = fabs(target_y-pos_y)
                if (distx_cs**2 + disty_cs**2) <= 625:  # 如果目标在以中心为圆心，25像素为半径的圆
                    bombthread_cs = threading.Thread(target=bomb_func)
                    print("Bomb CamShift", end=': ')
                    print(target_x, target_y)
                    bombthread_cs.start()
                    bombthread_cs.join()
                img2 = cv2.polylines(frame,[pts],True, 255,2)


            if show_default_results:  # 窗口的fps可用于评估性能
                fps = 1/(t1-t0)
                cv2.putText(frame,':{0}'.format(float('%.1f'%fps)),(0,50),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.circle(frame, (pos_x, pos_y), 25, (255, 0, 0), 2)

            if selectObject == True and ws>0 and hs>0:
                cv2.imshow('imshow1',frame[ys:ys+hs,xs:xs+ws])
                cv2.bitwise_not(frame[ys:ys+hs,xs:xs+ws],frame[ys:ys+hs,xs:xs+ws])

            if show_default_results:
                cv2.imshow('RANX_AI', frame)    
            # cv2.imshow('imshow',frame)
            if  cv2.waitKey(10)==27:  # 等待10s，按ESC退出
                break

    return xywh


if __name__ == "__main__":
    xywh = startdetect()
    if show_default_results:
        if cv2.waitKey(1) & 0xFF == ord('q'):  
            cv2.destroyAllWindows()
