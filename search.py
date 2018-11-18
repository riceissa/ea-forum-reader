#!/usr/bin/env python3

import sys
import json
import re
import requests
from urllib.parse import quote

import util

ALGOLIA_URL = ""


def highlighted_search_string(body, string):
    # body is already html escaped, so we need string to be on the same level
    esc_str = util.htmlescape(string)

    highlighted = r'''<span style="background-color: #ffff00;">\1</span>'''
    return re.sub("(" + re.escape(esc_str) + ")", highlighted, body, flags=re.IGNORECASE)


def search_posts(string):
    data = '''{"requests":[{"indexName":"test_posts","params":"query=%s&hitsPerPage=30&page=0"}]}''' % quote(string)
    r = requests.post(ALGOLIA_URL, data=data)

    return r.json()['results'][0]['hits']


def search_comments(string):
    data = '''{"requests":[{"indexName":"test_comments","params":"query=%s&hitsPerPage=30&page=0"}]}''' % quote(string)
    r = requests.post(ALGOLIA_URL, data=data)

    return r.json()['results'][0]['hits']


def show_comment(comment, string):
    result = ('''<div style="border: 1px solid #B3B3B3; margin: 10px; padding: 10px; background-color: #ECF5FF;">comment by <a href="./users.php?userid=%s">%s</a>
        on <a href="./posts.php?id=%s">%s</a>
        · <a href="./posts.php?id=%s#%s">%s</a>
        · score: %s
        ''' % (comment['userId'],
               comment['authorUserName'],
               comment['postId'],
               util.htmlescape(comment['postTitle']),
               comment['postId'],
               comment['_id'],
               comment['postedAt'],
               comment['baseScore']))

    result += '''<pre style="font-family: Lato, Helvetica, sans-serif; word-wrap: break-word; white-space: pre-wrap; white-space: -moz-pre-wrap;">%s</pre>\n''' % highlighted_search_string(util.htmlescape(comment['body']), string)
    result += "</div>"

    return result


def show_post(post, string, seen):
    result = ('''<div style="border: 1px solid #B3B3B3; margin: 10px; padding: 10px; background-color: #ECF5FF;"><a href="./posts.php?id=%s">%s</a>
    by <a href="./users.php?userid=%s">%s</a> · %s · score: %s
    ''' % (post['_id'],
           util.htmlescape(post['title']),
           post['userId'],
           post['authorUserName'],
           post['postedAt'],
           post['baseScore']))
    if string.lower() in post['body'].lower():
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
