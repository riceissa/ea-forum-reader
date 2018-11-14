#!/usr/bin/env python3

import sys
from scrape import *

if len(sys.argv) != 2 + 1:
    print("Unexpected number of arguments")
else:
    if sys.argv[2] == "rss":
        print(feed_for_user(sys.argv[1]))
    else:
        print(html_page_for_user(username=sys.argv[1], display_format=sys.argv[2]))
