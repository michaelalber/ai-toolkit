# <AI-Generated START>
import store
import users


def place_order(user_id, items):
    """items: list of (price, qty). Raises KeyError for an unknown user."""
    users.get_user(user_id)
    oid = len(store.rows("orders")) + 1
    store.put("orders", oid, {"user_id": user_id, "items": list(items)})
    return oid
# <AI-Generated END>
