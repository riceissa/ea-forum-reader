#!/usr/bin/env python3

import sys
from scrape import *

if len(sys.argv) <= 2:
    print("Need more args")
else:
    print(show_daily_posts(offset=int(sys.argv[1]), view=sys.argv[2]))
