#!/usr/bin/env python3

import sys
import json
import re
import requests
from urllib.parse import quote

import util
import linkpath
import config

ALGOLIA_URL = ""


def highlighted_search_string(body, string):
    # Body is already html escaped, so we need string to be on the same level.
    # Also, we need to escape and then highlight, because if we highlight and
    # then escape, the highlighting tag will also be escaped.
    search_terms = set(map(util.htmlescape, string.lower().split()))

    result = ""
    pat = re.compile(r'\w+|\W')

    for word in pat.findall(body):
        if word.lower() in search_terms:
            result += '<span style="background-color: #ffff00;">' + word + '</span>'
        else:
            result += word

    return result


def search_posts(string):
    data = '''{"requests":[{"indexName":"test_posts","params":"query=%s&hitsPerPage=30&page=0"}]}''' % quote(string)
    r = requests.post(ALGOLIA_URL, data=data)

    return r.json()['results'][0]['hits']


def search_comments(string):
    data = '''{"requests":[{"indexName":"test_comments","params":"query=%s&hitsPerPage=30&page=0"}]}''' % quote(string)
    r = requests.post(ALGOLIA_URL, data=data)

    return r.json()['results'][0]['hits']


def show_comment(comment, string):
    if 'authorUserName' in comment:
        user = util.safe_get(comment, 'authorUserName')
    elif 'authorSlug' in comment:
        user = util.safe_get(comment, 'authorSlug')
    else:
        user = util.safe_get(comment, 'authorDisplayName')
    result = ('''<div style="border: 1px solid #B3B3B3; margin: 10px; padding: 10px; background-color: %s;">comment by <a href="./users.php?userid=%s">%s</a>
        on <a href="./posts.php?id=%s">%s</a>
        · <a href="./posts.php?id=%s#%s">%s</a>
        ''' % (config.COMMENT_COLOR,
               comment['userId'],
               user,
               comment['postId'],
               util.htmlescape(comment['postTitle']),
               comment['postId'],
               comment['_id'],
               comment['postedAt']))

    result += '''<pre style="font-family: Lato, Helvetica, sans-serif; word-wrap: break-word; white-space: pre-wrap; white-space: -moz-pre-wrap;">%s</pre>\n''' % highlighted_search_string(util.htmlescape(comment['body']), string)
    result += "</div>"

    return result


def show_post(post, string, seen):
    if 'authorUserName' in post:
        user = post['authorUserName']
    elif 'authorSlug' in post:
        user = post['authorSlug']
    else:
        user = post['authorDisplayName']
    url = linkpath.posts(util.safe_get(post, ['_id']), util.safe_get(post, ['slug']))
    result = ('''<div style="border: 1px solid #B3B3B3; margin: 10px; padding: 10px; background-color: %s;"><a href="%s">%s</a>
    by %s · %s
    ''' % (config.COMMENT_COLOR,
           url,
           util.htmlescape(post['title']),
           util.userlink(
               slug=util.safe_get(post, ['authorSlug']),
               display_name=util.safe_get(post, ['authorDisplayName'])
           ),
           post['postedAt']))
    matched_in_body = False
    if 'body' in post:
        for term in string.split():
            # Check if any of the search terms is in the body
            if term.lower() in util.safe_get(post, 'body', default="").lower():
                matched_in_body = True
    if matched_in_body:
        result += '''<pre style="font-family: Lato, Helvetica, sans-serif; word-wrap: break-word; white-space: pre-wrap; white-space: -moz-pre-wrap;">%s</pre>\n''' % highlighted_search_string(util.htmlescape(post['body']), string)
    else:
        if post['_id'] in seen:
            # If we didn't even match inside the body and we've seen this post
            # before, it's a garbage result, so return nothing
            return ""

    seen.add(post['_id'])

    result += "</div>\n"
    return result

def print_comments(string):
    for comment in search_comments(string):
        print(show_comment(comment, string))

def print_posts(string):
    seen = set()
    for post in search_posts(string):
        print(show_post(post, string, seen))


if __name__ == "__main__":
    arg_count = 2

    if len(sys.argv) != arg_count + 1:
        print("Unexpected number of args")
        sys.exit()

    with open(sys.argv[1], "r") as f:
        ALGOLIA_URL = next(f).strip()

    search_string = sys.argv[2]
    print(''' <!DOCTYPE html>
        <html>''')
    print(util.show_head(search_string))
    print("<body>")
    print(util.show_navbar(search_value=search_string))
    print('''<div id="wrapper">''')
    print('''<div id="content">''')
    print('''<ul>
                <li><a href="#posts">Jump to post results</a></li>
                <li><a href="#comments">Jump to comment results</a></li>
            </ul>''')
    print('''<h2 id="posts">Post results</h2>''')
    print_posts(search_string)
    print('''<h2 id="comments">Comment results</h2>''')
    print_comments(search_string)
    print("</div>")
    print("</div>")
    print('''</body>
        </html>''')
