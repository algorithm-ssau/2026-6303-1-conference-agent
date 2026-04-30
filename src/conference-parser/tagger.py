import re
from config import TAG_RULES


def _normalize(text: str) -> str:
    text = (text or "").lower().replace("ё", "е")
    text = re.sub(r"\s+", " ", text)
    return text

def assign_hashtags(event_name: str = "", topics=None, raw_text: str = "", max_tags: int = 4) -> str:
    topics = topics or []
    haystack = _normalize(" ".join([event_name, raw_text, " ".join(topics)]))

    scored = []
    for tag, keywords in TAG_RULES.items():
        score = 0
        for kw in keywords:
            kw_n = _normalize(kw)
            if kw_n and kw_n in haystack:
                score += 1
        if score > 0:
            scored.append((score, tag))

    scored.sort(reverse=True)
    chosen = [tag for _, tag in scored[:max_tags]]

    return "; ".join(chosen) if chosen else "#прочее"