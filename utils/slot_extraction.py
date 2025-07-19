import dateparser
from datetime import datetime, timedelta

def extract_time_window(user_prompt):
    """
    Parses time window from user query and returns number of days.
    Defaults to 30 days if no clear window found.
    """
    user_prompt = user_prompt.lower()
    now = datetime.now()
    
    # Try parsing direct durations like "last 15 days"
    match = dateparser.parse(user_prompt, settings={'RELATIVE_BASE': now})
    if match:
        delta_days = (now - match).days
        if delta_days > 0:
            return delta_days

    # Fallbacks for common phrases
    if "last week" in user_prompt or "past week" in user_prompt:
        return 7
    if "last month" in user_prompt or "past month" in user_prompt:
        return 30
    if "fortnight" in user_prompt or "last fortnight" in user_prompt:
        return 14
    
    # Default
    return 30
