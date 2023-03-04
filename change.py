import os
import json

PATH = os.path.join("output", "Substitutions.txt")

API_JSON = os.path.join("output", "Substitutions.json")

NEW = {
    "EXP": "EXP\n"
}
# 末尾必须是\n，用于强制替换翻译文本


def load():
    with open(PATH, "r", encoding="utf-8") as fn:
        ori = fn.readlines()

    ori_dict = {}
    for i in ori:
        tmp = i.split("=")
        L = len(tmp)
        J = tmp[0:int(L/2)]
        K = tmp[int(L/2):L]
        j = ""
        k = ""
        for i in J:
            j += i
            j += "="
        for i in K:
            k += i
            k += "="
        j = j[:-1]
        k = k[:-1]
        ori_dict[j] = k
    return ori_dict


def save(fin_dict):
    with open(PATH, "w", encoding="utf-8") as fn:
        for i in fin_dict:
            fn.write(i+"="+fin_dict[i])


def change(ori_dict, new=NEW):
    for i in new:
        ori_dict[i] = new[i]
    return ori_dict


save(change(load()))

with open(API_JSON, "w") as f:
    json.dump(load(), f)
