# <AI-Generated START>
import re


def top_n(text, n):
    counts = {}
    for w in re.findall(r"[a-z']+", text.lower()):
        counts[w] = counts.get(w, 0) + 1
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:n]
# <AI-Generated END>
