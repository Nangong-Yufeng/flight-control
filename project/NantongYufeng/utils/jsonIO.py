import json

def get_tar_pos():
    try:
        tar_pos = json.load(open("tar_pos_json.json", "r"))
        print(tar_pos)
        return tar_pos
    except FileNotFoundError:
        print("没这个文件捏")
    