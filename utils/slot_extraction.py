import re
import dateparser
from datetime import datetime
from rapidfuzz import fuzz

_WORD_NUM = {
    "one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10,
    "eleven":11,"twelve":12,"thirteen":13,"fourteen":14,"fifteen":15,"sixteen":16,"seventeen":17,
    "eighteen":18,"nineteen":19,"twenty":20,"thirty":30,"forty":40,"fifty":50,"sixty":60,
    "seventy":70,"eighty":80,"ninety":90,"hundred":100
}

def _word_to_num(text: str):
    tokens = text.replace("-", " ").split()
    total, cur = 0, 0
    for t in tokens:
        if t not in _WORD_NUM:
            continue
        v = _WORD_NUM[t]
        if v == 100:
            cur = max(1, cur) * 100
        else:
            cur += v
    total += cur
    return total if total > 0 else None

def _near(token: str, targets, threshold=80):
    return any(fuzz.ratio(token, t) >= threshold for t in targets)

def extract_time_window(user_prompt: str):
    """
    Returns number of days inferred from user_prompt.
    Fuzzy-robust against typos + supports numeric and word durations.
    Returns None if no window found (caller can default).
    """
    s = (user_prompt or "").lower().strip()
    now = datetime.now()

    # tokenize words/numbers
    tokens = re.findall(r"[a-z0-9]+", s)

    # detect approx "last/past/previous"
    has_window_word = any(_near(t, ["last", "past", "previous", "prev"]) for t in tokens)

    # detect approx unit
    unit_map = {"day": 1, "week": 7, "month": 30, "year": 365}
    unit = None
    for t in tokens:
        for u in unit_map.keys():
            if _near(t, [u, u + "s"]):
                unit = u
                break
        if unit:
            break

    # detect numeric value
    num = None
    for t in tokens:
        if t.isdigit():
            num = int(t)
            break

    # detect word-number value if no digit
    if num is None:
        num = _word_to_num(" ".join(tokens))

    # fuzzy duration like "lats 15 dyas"
    if has_window_word and unit and num:
        return num * unit_map[unit]

    # relative date like "15 days ago", "yesterday"
    rel = dateparser.parse(s, settings={"RELATIVE_BASE": now})
    if rel:
        delta_days = (now - rel).days
        if delta_days > 0:
            return delta_days

    # phrase fallbacks
    if any(_near(t, ["fortnight"]) for t in tokens):
        return 14
    if any(_near(t, ["yesterday"]) for t in tokens):
        return 1
    if "this week" in s:
        return 7
    if "this month" in s:
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return max(1, (now - start).days)

    return None
