# <AI-Generated START>
import itertools

import store

_ids = itertools.count(1)


def create_user(name):
    uid = next(_ids)
    store.put("users", uid, {"name": name})
    return uid


def get_user(uid):
    return store.get("users", uid)
# <AI-Generated END>
