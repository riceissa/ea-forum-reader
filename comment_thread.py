#!/usr/bin/env python3

import sys
from scrape import *

if len(sys.argv) <= 1:
    print("Please enter a post ID as argument")
else:
    print(print_post_and_comment_thread(sys.argv[1]))

