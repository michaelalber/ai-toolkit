# <AI-Generated START>
def coerce(value):
    """Convert a raw value string to str/bool/int/float."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    if value.lower() in ("true", "false"):
        return bool(value)
    for kind in (int, float):
        try:
            return kind(value)
        except ValueError:
            pass
    return value
# <AI-Generated END>
