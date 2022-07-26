from pathlib import Path
import cv2
import torch
import torch.backends.cudnn as cudnn
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
weights = 'yolov5s.pt'
#模型尺寸
imgsz = 640

show_default_results = True#是否观看默认结果

src = '0'  # 从摄像头读取视频输入

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


def startdetect():
    if show_default_results:
        seen = 0
    source = str(src)
    webcam = source.isnumeric() or source.endswith('.txt') or source.lower().startswith(
        ('rtsp://', 'rtmp://', 'http://', 'https://'))
    cudnn.benchmark = True  # set True to speed up constant image size inference
    dataset = LoadStreams(source, img_size=imgsz, stride=stride, auto=pt)
    bs = len(dataset)  # batch_size
    for path, img, im0s, vid_cap in dataset:
        img = torch.from_numpy(img).to(device)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img = img / 255.0  # 0 - 255 to 0.0 - 1.0
        if len(img.shape) == 3:
            img = img[None]  # expand for batch dim
        pred = model(img, augment=False, visualize=False)[0]
        #apple NMS
        pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)

        for i, det in enumerate(pred):  # per image
            if show_default_results:
                seen += 1
            s = ''
            s += '%gx%g ' % img.shape[2:]
            img0 = im0s[i].copy()
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
                    annotator.box_label(xyxy, label=label, color=(0,0,0))#目标框

            if show_default_results:
                im0 = annotator.result()

            if show_default_results:
                cv2.imshow('RANX_AI', im0)

    return xywh


if __name__ == "__main__":
    xywh = startdetect()
    if show_default_results:
        if cv2.waitKey(1) & 0xFF == ord('q'):  
            cv2.destroyAllWindows()
