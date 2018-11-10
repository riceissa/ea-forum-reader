#!/usr/bin/env python3

import sys
from scrape import *

if len(sys.argv) <= 2:
    print("Please enter a username and a format as arguments")
else:
    if sys.argv[2] == "rss":
        print(feed_for_user(sys.argv[1]))
    else:
        print(html_page_for_user(sys.argv[1]))
