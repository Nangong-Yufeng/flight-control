"""
用于把坐标点（Point类的形式）与json文件相互转化
（还没完工，且已搁置）
"""

import json


class Point:
    def __init__(self, latitude_deg, longitude_deg, altitude_m):
        self.latitude_deg = latitude_deg
        self.longitude_deg = longitude_deg
        self.altitude_m = altitude_m


def trans(point):
    return {
        "纬度latitude_deg": point.latitude_deg,
        "经度longitude_deg": point.longitude_deg,
        "海拔altitude_m": point.altitude_m
    }


def write(fp=None):
    wpoints = [{"point1": Point(0.1, 0.1, 0.1)},
               {"point2": Point(0.2, 0.2, 0.2)},
               {"point3": Point(0.3, 0.3, 0.3)}]
    if fp is None:
        f = open("../points.json", 'w')
    else:
        f = fp
    json.dump(wpoints,
              f,
              indent=4,
              separators=(',', ":"),
              default=trans,
              ensure_ascii=False
              )


def read(fp=None):
    if fp is None:
        f = open("../points.json", 'r')
    else:
        f = fp
    rpoints = json.load(f)
    return rpoints


if __name__ == '__main__':
    points = read()
    print("type of points:" + str(type(points)))
    print(points[1])
    print(type(points[1]))
