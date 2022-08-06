import json


class Point:
    def __init__(self, latitude_deg, longitude_deg, altitude_m):
        self.latitude_deg = latitude_deg
        self.longitude_deg = longitude_deg
        self.altitude_m = altitude_m


def trans(point):
    return {
        "latitude_deg": point.latitude_deg,
        "longitude_deg": point.longitude_deg,
        "altitude_m": point.altitude_m
    }


def main():
    example = {"point": Point(0.1, 0.2, 0.3)}
    f = open("../example.json", 'w')
    json.dump(example, f, default=trans)


if __name__ == '__main__':
    main()
