#!/usr/bin/env python3

import sys
from scrape import *

if len(sys.argv) != 2 + 1:
    print("Please enter a post ID as argument")
else:
    print(print_post_and_comment_thread(postid=sys.argv[1], display_format=sys.argv[2]))

