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


def write():
    example = [{"point1": Point(0.1, 0.1, 0.1)},
               {"point2": Point(0.2, 0.2, 0.2)},
               {"point3": Point(0.3, 0.3, 0.3)}]
    f = open("../points.json", 'w')
    json.dump(example,
              f,
              indent=4,
              separators=(',', ":"),
              default=trans,
              ensure_ascii=False
              )

def read():
    # todo:)

if __name__ == '__main__':
    ()
