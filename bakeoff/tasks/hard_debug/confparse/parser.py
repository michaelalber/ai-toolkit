# <AI-Generated START>
from .coerce import coerce
from .lexer import strip_comment


def load(text):
    """Parse INI-like text into nested dicts; [a.b] sections create nested dicts."""
    root = {}
    current = root
    for raw in text.splitlines():
        if raw.lstrip().startswith("["):
            line = raw.strip()
            if line.endswith("]"):
                current = root
                for part in line[1:-1].split("."):
                    current = current.setdefault(part, {})
                continue
        line = strip_comment(raw).strip()
        if not line:
            continue
        key, _, value = line.partition("=")
        current[key.strip()] = coerce(value.strip())
    return root
# <AI-Generated END>
