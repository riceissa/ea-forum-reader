#!/usr/bin/env python3

import sys
from scrape import *

if len(sys.argv) != 4+1:
    print("Unexpected number of arguments")
else:
    print(show_daily_posts(offset=int(sys.argv[1]), view=sys.argv[2],
                           before=sys.argv[3], after=sys.argv[4]))
