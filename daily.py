#!/usr/bin/env python3

import sys
from scrape import *

if len(sys.argv) <= 1:
    print(show_daily_posts())
else:
    try:
        print(show_daily_posts(offset=int(sys.argv[1])))
    except ValueError:
        print(show_daily_posts())
