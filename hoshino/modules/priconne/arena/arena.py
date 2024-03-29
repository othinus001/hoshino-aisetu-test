import base64
import os
import time
from collections import defaultdict

from hoshino import aiorequests, config, util

from .. import chara
from . import sv

try:
    import ujson as json
except:
    import json

from os.path import dirname, join, exists
from os import remove
from asyncio import Lock

querylock = Lock()

logger = sv.logger

"""
Database for arena likes & dislikes
DB is a dict like: { 'md5_id': {'like': set(qq), 'dislike': set(qq)} }
"""
DB_PATH = os.path.expanduser("~/.hoshino/arena_db.json")
DB = {}
try:
    with open(DB_PATH, encoding="utf8") as f:
        DB = json.load(f)
    for k in DB:
        DB[k] = {
            "like": set(DB[k].get("like", set())),
            "dislike": set(DB[k].get("dislike", set())),
        }
except FileNotFoundError:
    logger.warning(f"arena_db.json not found, will create when needed.")


def dump_db():
    """
    Dump the arena databese.
    json do not accept set object, this function will help to convert.
    """
    j = {}
    for k in DB:
        j[k] = {
            "like": list(DB[k].get("like", set())),
            "dislike": list(DB[k].get("dislike", set())),
        }
    with open(DB_PATH, "w", encoding="utf8") as f:
        json.dump(j, f, ensure_ascii=False)


def get_likes(id_):
    return DB.get(id_, {}).get("like", set())


def add_like(id_, uid):
    e = DB.get(id_, {})
    l = e.get("like", set())
    k = e.get("dislike", set())
    l.add(uid)
    k.discard(uid)
    e["like"] = l
    e["dislike"] = k
    DB[id_] = e


def get_dislikes(id_):
    return DB.get(id_, {}).get("dislike", set())


def add_dislike(id_, uid):
    e = DB.get(id_, {})
    l = e.get("like", set())
    k = e.get("dislike", set())
    l.discard(uid)
    k.add(uid)
    e["like"] = l
    e["dislike"] = k
    DB[id_] = e


_last_query_time = 0
quick_key_dic = {}  # {quick_key: true_id}


def refresh_quick_key_dic():
    global _last_query_time
    now = time.time()
    if now - _last_query_time > 300:
        quick_key_dic.clear()
    _last_query_time = now


def gen_quick_key(true_id: str, user_id: int) -> str:
    qkey = int(true_id[-6:], 16)
    while qkey in quick_key_dic and quick_key_dic[qkey] != true_id:
        qkey = (qkey + 1) & 0xFFFFFF
    quick_key_dic[qkey] = true_id
    mask = user_id & 0xFFFFFF
    qkey ^= mask
    return base64.b32encode(qkey.to_bytes(3, "little")).decode()[:5]


def get_true_id(quick_key: str, user_id: int) -> str:
    mask = user_id & 0xFFFFFF
    if not isinstance(quick_key, str) or len(quick_key) != 5:
        return None
    qkey = (quick_key + "===").encode()
    qkey = int.from_bytes(base64.b32decode(qkey, casefold=True, map01=b"I"), "little")
    qkey ^= mask
    return quick_key_dic.get(qkey, None)


from .pcrdapi import callPcrd
async def do_query(id_list, user_id, region=1, raw=0):
    defen = id_list
    key = ''.join([str(x) for x in sorted(defen)]) + str(region)
    value = int(time.time())

    curpath = dirname(__file__)
    bufferpath = join(curpath, 'buffer/buffer.json')

    buffer = {}
    with open(bufferpath, 'r', encoding="utf-8") as fp:
        buffer = json.load(fp)

    if (value - buffer.get(key, 0) < 259200) and (exists(join(curpath, f'buffer/{key}.json'))):  # 三天内查询过 直接返回
        with open(join(curpath, f'buffer/{key}.json'), 'r', encoding="utf-8") as fp:
            result = json.load(fp)
    else:  # 尝试查询；若失败，尝试降级，返回缓存结果；若无缓存，寄
        degrade_result = None
        if exists(join(curpath, f'buffer/{key}.json')):
            with open(join(curpath, f'buffer/{key}.json'), 'r', encoding="utf-8") as fp:
                degrade_result = json.load(fp)

        isquerysucceed = True
        id_list = [x * 100 + 1 for x in id_list]

        if querylock.locked():
            await asyncio.sleep(5)
        async with querylock:
            try:
                res = await callPcrd(id_list, 1, region, 1)
                logger.debug(f"len(res)={len(res)}")
            except Exception as e:
                logger.exception(e)
                isquerysucceed = False
                if degrade_result:
                    result = degrade_result
                else:
                    return None

            if res["code"]:
                isquerysucceed = False
                if degrade_result:
                    result = degrade_result
                else:
                    raise aiorequests.HTTPError(response=res)

            result = res.get("data", {}).get("result")
            if result is None:
                isquerysucceed = False
                if degrade_result:
                    result = degrade_result
                else:
                    return None

            if isquerysucceed:
                buffer[key] = value

                with open(bufferpath, 'w', encoding="utf-8") as fp:
                    json.dump(buffer, fp, ensure_ascii=False, indent=4)

                homeworkpath = join(curpath, f'buffer/{key}.json')
                with open(homeworkpath, 'w', encoding="utf-8") as fp:
                    json.dump(result, fp, ensure_ascii=False, indent=4)

    ret = []
    for entry in result:
        eid = entry["id"]
        likes = get_likes(eid)
        dislikes = get_dislikes(eid)
        ret.append({
            "qkey": gen_quick_key(eid, user_id),
            "atk": [chara.fromid(c["id"] // 100, c["star"], c["equip"]) for c in entry["atk"]],
            "def": [chara.fromid(c["id"] // 100, c["star"], c["equip"]) for c in entry["def"]],
            "up": entry["up"],
            "down": entry["down"],
            "my_up": len(likes),
            "my_down": len(dislikes),
            "user_like": 1 if user_id in likes else -1 if user_id in dislikes else 0,
        })

    return ret


async def do_like(qkey, user_id, action):
    true_id = get_true_id(qkey, user_id)
    if true_id is None:
        raise KeyError
    add_like(true_id, user_id) if action > 0 else add_dislike(true_id, user_id)
    dump_db()
    # TODO: upload to website
