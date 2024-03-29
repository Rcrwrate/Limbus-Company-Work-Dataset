import os
import json
import traceback
import copy
from log import Log

l = Log("run", log_path="output")


def get_or(di, name, default=None):
    try:
        return di[name]
    except KeyError:
        return default


def is_Chinese(word):
    if isinstance(word, int):
        return False
    for ch in word:
        try:
            if '\u4e00' <= ch <= '\u9fff':
                return True
        except:
            # l.info(f"[INFO]:\t{ch} check chinese error")
            pass  # 存在列表嵌套的问题
    return False


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
            # li.append("{}{}".format(parent, filename))
            li.append(os.path.join(parent, filename))


OL = {}
get_list_json("./Assets/", OL)


def get_path(new_path):
    "获取CN对应的EN,JP,KR文件位置"
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
get_list_new("./LimbusLocalize/Localize/CN/", NL)


def fetch_json(ori):
    "根据文件位置读取JSON"
    fin = get_path(ori)
    for i in fin:
        try:
            with open(fin[i], "r", encoding="utf-8") as f:
                fin[i] = json.load(f)
        except:  # 你很神奇，为什么这还能报个错
            l.error(f"[ERROR]\t{fin[i]} load error")
            with open(fin[i], "r", encoding="utf-8") as f:
                fin[i] = eval(f.read())
    return fin


def transform(data):
    "将双重嵌套字典变成单层和重建编号ID"
    keys = list(data.keys())
    if len(data[keys[0]]["dataList"]) == len(data[keys[1]]["dataList"]) == len(data[keys[-1]]["dataList"]) == len(data[keys[-2]]["dataList"]):
        out = copy.deepcopy(data)
        for i in keys:
            j = 0
            remove = []
            while j < len(data[i]["dataList"]):
                out[i]["dataList"][j]["id"] = j
                for k in data[i]["dataList"][j]:
                    if isinstance(data[i]["dataList"][j][k], (str, int)):
                        pass
                    elif isinstance(data[i]["dataList"][j][k], list):
                        for h in data[i]["dataList"][j][k]:
                            for q in h.keys():
                                out[i]["dataList"][j][f"{k}-{q}"] = h[q]
                        remove.append({"i": i, "j": j, "k": k})
                    # 未经过测试，看这段代码是不是血压很高啊，没错，我也是
                    elif isinstance(data[i]["dataList"][j][k], dict):
                        for q in data[i]["dataList"][j][k].keys():
                            out[i]["dataList"][j][f"{k}-{q}"] = data[i]["dataList"][j][k][q]
                        remove.append({"i": i, "j": j, "k": k})
                j += 1
            for one in remove:
                del out[one["i"]]["dataList"][one["j"]][one["k"]]
        return out
    else:
        return data  # 不修改


def merge(fin, out: dict = {}):
    "融合翻译,根据ID(存在ID不存在的问题和列表嵌套的问题)"
    for i in fin["CN"]["dataList"]:
        try:
            id = i["id"]
            out[id] = {}
            for key in fin.keys():
                for j in fin[key]["dataList"]:
                    if j["id"] == id:
                        out[id][key] = {}
                        for k in j:
                            if k != "id":
                                out[id][key][k] = j[k]
        except:
            pass  # 存在ID不存在的条目，暂时忽略
    return out


def check(out, last={}):
    "检查和写入最终JSON"
    for i in out:
        for j in out[i]["CN"]:
            CN = out[i]["CN"][j]
            if is_Chinese(CN):
                try:
                    for key in ["EN", "JP", "KR"]:
                        last[out[i][key][j]] = CN
                except:
                    pass  # 翻译语种缺失忽略
    return last


def main():
    last = {}
    for i in NL:
        print(i)
        try:
            last = check(merge(transform(fetch_json(i))), last)
        except Exception as e:
            l.critical(f"[critical]\t{i}\n\t{traceback.format_exc()}")
        print(len(last))
    save(last)


def save(fin_dict, PATH=os.path.join("output", "Substitutions.txt")):
    with open(PATH, "w", encoding="utf-8") as fn:
        for i in fin_dict:
            fn.write(i.replace("\n", "\\n")+"=" +
                     fin_dict[i].replace("\n", "\\n")+"\n")


if __name__ == "__main__":
    main()
