import os
import json
import traceback
from log import Log

l = Log("run", log_path="output")


def get_or(di, name, default=None):
    try:
        return di[name]
    except KeyError:
        return default


def is_Chinese(word):
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
            li.append("{}{}".format(parent, filename))


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
get_list_new("./LimbusLocalize/assets/Localize/CN/", NL)


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
            last = check(merge(fetch_json(i)), last)
        except Exception as e:
            l.critical(f"[critical]\t{i}\n\t{traceback.format_exc()}")
        print(len(last))
    save(last)


def save(fin_dict, PATH=os.path.join("output", "_Substitutions.txt")):
    with open(PATH, "w", encoding="utf-8") as fn:
        for i in fin_dict:
            fn.write(i+"="+fin_dict[i]+"\n")


f = "./LimbusLocalize/assets/Localize/CN/CN_S0_23.json"

# print(get_path(f))
print(check(merge(fetch_json(f))))
# main()
