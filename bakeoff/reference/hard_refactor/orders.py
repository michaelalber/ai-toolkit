# <AI-Generated START>
import users


def place_order(repo, user_id, items):
    users.get_user(repo, user_id)
    oid = repo.next_id("orders")
    repo.put("orders", oid, {"user_id": user_id, "items": list(items)})
    return oid
# <AI-Generated END>
