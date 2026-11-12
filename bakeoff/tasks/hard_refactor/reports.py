# <AI-Generated START>
import store


def user_order_totals():
    """Return {user name: total spent}."""
    names = {uid: u["name"] for uid, u in store.rows("users").items()}
    totals = {}
    for o in store.rows("orders").values():
        name = names[o["user_id"]]
        totals[name] = totals.get(name, 0) + sum(p * q for p, q in o["items"])
    return totals
# <AI-Generated END>
