# <AI-Generated START>
DB = {}


def put(table, key, value):
    DB.setdefault(table, {})[key] = value


def get(table, key):
    return DB[table][key]


def rows(table):
    return dict(DB.get(table, {}))
# <AI-Generated END>
