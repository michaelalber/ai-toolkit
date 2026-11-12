# <AI-Generated START>
def create_user(repo, name):
    uid = repo.next_id("users")
    repo.put("users", uid, {"name": name})
    return uid


def get_user(repo, uid):
    return repo.get("users", uid)
# <AI-Generated END>
