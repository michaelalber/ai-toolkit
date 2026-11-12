# <AI-Generated START>
from .coerce import coerce
from .lexer import strip_comment


def load(text):
    root = {}
    current = root
    for raw in text.splitlines():
        line = strip_comment(raw).strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            current = root
            for part in line[1:-1].split("."):
                current = current.setdefault(part, {})
            continue
        key, _, value = line.partition("=")
        current[key.strip()] = coerce(value.strip())
    return root
# <AI-Generated END>
