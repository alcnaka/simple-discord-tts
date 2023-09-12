import re


def clean_emoji(t: str) -> str:
    """Remove discord emoji from string.

    <:ika:446992338573852676> -> ''
    <:c_jett:868832655918137345> -> ''
    """
    return re.sub(r"<:.*[0-9]*>", "", t)


def clean_url(t: str) -> str:
    """Remove URL from string."""
    return re.sub(r"https?://[\w!?/+\-_~;.,*&@#$%()'[\]=]+", "", t)


def clean_text(t: str) -> str:
    t = clean_emoji(t)
    t = clean_url(t)
    return t.strip()
