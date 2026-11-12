# <AI-Generated START>
def user_order_totals(repo):
    names = {uid: u["name"] for uid, u in repo.rows("users").items()}
    totals = {}
    for o in repo.rows("orders").values():
        name = names[o["user_id"]]
        totals[name] = totals.get(name, 0) + sum(p * q for p, q in o["items"])
    return totals
# <AI-Generated END>
