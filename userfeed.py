#!/usr/bin/env python3

import sys
from scrape import *

if len(sys.argv) <= 1:
    print("Please enter a username as argument")
else:
    print(feed_for_user(sys.argv[1]))
