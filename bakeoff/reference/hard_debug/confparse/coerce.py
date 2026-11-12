# <AI-Generated START>
import re

_NUM = re.compile(r"^-?\d+(\.\d+)?$")


def coerce(value):
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if _NUM.match(value):
        return float(value) if "." in value else int(value)
    return value
# <AI-Generated END>
