import re


def clean_emoji(t: str) -> str:
    """_summary_
    <:ika:446992338573852676> -> ''
    <:c_jett:868832655918137345> -> ''
    """
    return re.sub(r"<:.*[0-9]*>", "", t)

def clean_text(t: str) -> str:
    t = clean_emoji(t)
    return t
