from types import FunctionType
import os
import json
from log import Log

l = Log("run", log_path="output")


def get_or(di, name, default=None):
    try:
        return di[name]
    except KeyError:
        return default


def get_list_json(path: str, li: dict):
    current_address = path
    for parent, dirnames, filenames in os.walk(current_address):
        for dirname in dirnames:
            pass
        for filename in filenames:
            li[filename] = parent


def get_list_new(path: str, li: list):
    current_address = path
    for parent, dirnames, filenames in os.walk(current_address):
        for dirname in dirnames:
            pass
        for filename in filenames:
            li.append("{}{}".format(parent, filename))


OL = {}
get_list_json("./Assets/", OL)


def get_path(new_path):
    name = os.path.split(new_path)[1]
    fin = {"CN": new_path}
    for i in ["EN", "JP", "KR"]:
        try:
            N = name.replace("CN", i)
            NN = get_or(OL, N, None)
            if NN:
                fin[i] = os.path.join(NN, N)
        except:
            l.error(f"[ERROR]:\t{name} in {i} not found!")
    return fin


NL = []
get_list_new("./LimbusLocalize/assets/Localize/CN/", NL)


def fetch_json(ori):
    fin = get_path(ori)
    for i in fin:
        try:
            with open(fin[i], "r", encoding="utf-8") as f:
                fin[i] = json.load(f)
        except:  # 你很神奇，为什么这还能报个错
            with open(fin[i], "r", encoding="utf-8") as f:
                fin[i] = eval(f.read())
    return fin


def merge(fin, out: dict = {}):
    for i in fin["CN"]["dataList"]:
        id = i["id"]
        out[id] = {}
        for key in fin.keys():
            for j in fin[key]["dataList"]:
                if j["id"] == id:
                    out[id][key] = {}
                    for k in j:
                        if k != "id":
                            out[id][key][k] = j[k]
    return out


print(merge(fetch_json("./LimbusLocalize/assets/Localize/CN/CN_Bufs.json")))
