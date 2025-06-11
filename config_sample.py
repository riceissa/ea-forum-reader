#!/usr/bin/env python3

from pathlib import Path

# Pick one
PATH_STYLE = "localhost"
# PATH_STYLE = "official"

GRAPHQL_URL = 'https://forum.effectivealtruism.org/graphql'
LINK_COLOR = "#326492"
COMMENT_COLOR = "#ECF5FF"
TITLE = "EA Forum Reader"

# GRAPHQL_URL = 'https://www.lesswrong.com/graphql'
# LINK_COLOR = "#6a8a6b"
# COMMENT_COLOR = "#F7F7F8"
# TITLE = "LessWrong 2.0 Reader"

EMAIL = ""
email_path = Path("../EMAIL.txt")
if not email_path.exists():
    raise FileNotFoundError("File not found! Please specify an email in EMAIL.txt.")

with open(email_path, "r") as f:
    EMAIL = next(f).strip()
    if not EMAIL:
        raise ValueError("Please specify an email in EMAIL.txt.")
