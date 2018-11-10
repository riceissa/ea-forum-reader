#!/usr/bin/env python3

import sys
from scrape import userid_to_userslug

# For some reason, the Algolia search result JSON only has the user ID and
# username, not the user slug.  So to be able to link to the user page from
# search results, we need to conver the userid to a user slug.

print(userid_to_userslug(sys.argv[1]))
