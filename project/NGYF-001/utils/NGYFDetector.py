import cv2 as cv
import numpy as np
import torch
import torch.nn as nn

class NGYFDetector:
    red_inner_lowerb = np.array([115, 70, 148])
    red_inner_uperb = np.array([204, 255, 255])
    red_outer_lowerb = np.array([0, 0, 166])
    red_outer_uperb = np.array([167, 75, 255])
    image_size = (28, 28)
    def __init__(self):
        self.net = torch.load('models\modelRC1.pth')
        self.net.eval()

    # 网络的推断, 传入的Image必须是经过pre_inference处理过的
    def inference(self, image):
        y = self.net(image)
        y = torch.argmax(y, dim=1)
        return y

    # 主操作, 将图片传入, 返回list
    # list中每个元素的内容: { 数字, (x, y) }
    def detect(self, image: np.ndarray) -> list:
        outer = NGYFDetector.preprocess(image)
        targets, pos = NGYFDetector.find_pantagon(image, outer)  # target是每一个被识别出来的标靶的图像
        digits = []
        single_nums = []
        nums = []
        for target in targets:
            x, y = NGYFDetector.matching_template(target)
            digits.append(cv.resize(x, NGYFDetector.image_size))
            digits.append(cv.resize(y, NGYFDetector.image_size))
        tensor_imgs = NGYFDetector.pre_inference(digits)
        for tensor_image in tensor_imgs:
            result = self.inference(tensor_image)
            single_nums.append(int(result))
        for i in range(0, len(single_nums), 2):
            nums.append(single_nums[i] * 10 + single_nums[i + 1])
            # nums.append(first_digit * 10 + second_digit)
        assert len(nums) == len(pos)
        return nums, pos
        
    # 下面的全部都是静态方法

    # 图像预处理, 主要是圈出两个方框
    @staticmethod
    def preprocess(img: np.ndarray) -> np.ndarray:
        img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        img = cv.GaussianBlur(img, (5, 5), 0)
        kernel = np.array([0, 1, 0, 1, 1, 1, 0, 1, 0], np.uint8)
        img = cv.erode(img, kernel, iterations=1)
        img = cv.dilate(img, kernel, iterations=1)

        # inner 标靶的红色部分
        # outer 标靶的白色外圈
        # 红色部分纯净, 但是不规则, 白色形状很好的保存下来了, 但是有干扰
        inner_img = cv.inRange(img, NGYFDetector.red_inner_lowerb, NGYFDetector.red_inner_uperb)
        outer_img = cv.inRange(img, NGYFDetector.red_outer_lowerb, NGYFDetector.red_outer_uperb)
        outer_img = NGYFDetector.determine_outer(inner_img, outer_img)
        return outer_img

    # 利用内圈确定外圈
    @staticmethod
    def determine_outer(inner: np.ndarray, outer: np.ndarray) -> np.ndarray:
        # 膨胀内圈来确定外圈
        kernel = np.ones((7, 7), np.uint8)
        flatten_inner = cv.dilate(inner, kernel, iterations=3)
        kernel = np.array([0, 1, 0, 1, 1, 1, 0, 1, 0], np.uint8)
        tmp = cv.bitwise_and(outer, flatten_inner)
        tmp = cv.dilate(tmp, kernel, iterations=3)
        tmp = cv.erode(tmp, kernel, iterations=2)
        return tmp

    # 防止上下颠倒
    @staticmethod
    def compute_orientation(contour: np.ndarray) -> bool:
        # get center of the contour 
        M = cv.moments(contour)
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        # get the farthest point
        dist = 0
        for i in range(len(contour)):
            x, y = contour[i][0]
            tmp = (x - cx) * (x - cx) + (y - cy) * (y - cy)
            if tmp > dist:
                dist = tmp
                far_x = x
        if far_x > cx:
            return True
        else:
            return False
    
    # 找出五边形的外接椭圆
    @staticmethod
    def find_pantagon_ellipse(img: np.ndarray, outer: np.ndarray) -> list:
        # find countour
        contours, hierarchy = cv.findContours(outer, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        find_contours = []
        for i in range(len(contours)):
            area = cv.contourArea(contours[i])
            if area > img.shape[0] * img.shape[1] * 0.0003:
                find_contours.append(contours[i])
        
        # using fitEllipse
        ellipse_points = []
        for i in range(len(find_contours)):
            if (len(find_contours[i]) < 5):
                continue
            ellipse = cv.fitEllipse(find_contours[i])
            ellipse_points.append(ellipse[0])
            ellipse_points.append(ellipse[1])
            # 调整圈出图像的方向(防止上下颠倒)
            if NGYFDetector.compute_orientation(find_contours[i]):
                ellipse_points.append(ellipse[2] + 180)    
            else:
                ellipse_points.append(ellipse[2])
        return ellipse_points

    # 将outer中的五边形取出, 并且返回原图像对应的部分
    @staticmethod
    def find_pantagon(img: np.ndarray, outer: np.ndarray) -> tuple:
        ellipse_points = NGYFDetector.find_pantagon_ellipse(img, outer)
        assert len(ellipse_points) % 3 == 0
        # cut sub image and rotate
        sub_images = []
        pos = []
        for i in range(0, len(ellipse_points), 3):
            center, size, angle = ellipse_points[i:i+3]
            center = tuple(map(int, center))
            size = tuple(map(int, size))
            assert size[0] > 0 and size[1] > 0
            angle = int(angle) + 180

            left = center[0] - size[0]
            if left < 0:
                left = 0
            right = center[0] + size[0]
            if right > img.shape[1]:
                right = img.shape[1]
            top = center[1] - size[1] // 2
            if top < 0:
                top = 0
            bottom = center[1] + size[1] // 2
            if bottom > img.shape[0]:
                bottom = img.shape[0]
            # cut image
            sub_img = img[top:bottom, left:right]
            M = cv.getRotationMatrix2D(((right - left) / 2, (bottom - top) / 2), angle, 1)
            sub_img = cv.warpAffine(sub_img, M, (right - left, bottom - top))
            sub_width = sub_img.shape[1]
            sub_height = sub_img.shape[0]
            sub_ratio = 3
            top = sub_width // sub_ratio
            bottom = sub_width // sub_ratio * (sub_ratio - 1)
            left = sub_height // sub_ratio
            right = sub_height // sub_ratio * (sub_ratio - 1)
            sub_img = sub_img[left:right, top:bottom]
            sub_images.append(sub_img)
            pos.append(center)
                
        return sub_images, pos
    
    # 模板匹配, 将标靶白色区域确定, 然后裁剪出两个数字
    @staticmethod
    def matching_template(img: np.ndarray) -> list:
        img = cv.GaussianBlur(img, (3, 3), 0)
        shape = img.shape
        magic = 0.7
        all_white_mat = np.ones((int(shape[0] * magic), int(shape[1] * magic), 3), np.uint8) * 255
        result = cv.matchTemplate(img, all_white_mat, cv.TM_SQDIFF)

        result_max = result.max()
        result = result / result_max * 255
        result = result.astype(np.uint8)
        
        # 获取模板匹配后目标位置
        _, _, min_loc, _ = cv.minMaxLoc(result)
        top_left = min_loc
        bottom_right = (top_left[0] + all_white_mat.shape[1], top_left[1] + all_white_mat.shape[0])

        # 经过测试, V通道的img区别效果最好
        v_img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        v_img = cv.split(v_img)[2]
        v_img = cv.equalizeHist(v_img)
        v_img = cv.bitwise_not(v_img)
        v_img = v_img[top_left[1]: bottom_right[1], top_left[0]: bottom_right[0]]

        magic0x1 = 0.55
        magic0x2 = 0.45
        left_margin = int(v_img.shape[1] * magic0x1)
        right_margin = int(v_img.shape[1] * magic0x2)
        a, b = v_img[:, :left_margin], v_img[:, right_margin:]
        # cv.waitKey(0)
        return (v_img[:, 0: left_margin], v_img[:, right_margin: img.shape[1]])
    
    # 送进网络前的预处理
    # 注意, 列表中的图像必须为单通道28x28
    @staticmethod
    def pre_inference(images: list) -> list:
        result = []
        for image in images:
            t_img = torch.tensor(image, dtype=torch.float32).cuda()
            t_img = torch.reshape(t_img, (1, 1, t_img.shape[0], t_img.shape[1]))
            result.append(t_img)
        return result
    
