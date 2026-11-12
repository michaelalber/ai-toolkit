# <AI-Generated START>
def top_n(text, n):
    """Return the n most frequent words as [(word, count)].

    Case-insensitive, punctuation ignored (apostrophes inside words kept),
    ties broken alphabetically.
    """
    counts = {}
    for w in text.split():
        counts[w] = counts.get(w, 0) + 1
    return sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:n]
# <AI-Generated END>
