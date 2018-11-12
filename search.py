#!/usr/bin/env python3

import sys
import json
import requests
from urllib.parse import quote
from scrape import htmlescape, show_navbar, show_head

ALGOLIA_URL = ""
with open(sys.argv[1], "r") as f:
    ALGOLIA_URL = next(f).strip()


def search_posts(string):
    data = '''{"requests":[{"indexName":"test_posts","params":"query=%s&hitsPerPage=30&page=0"}]}''' % quote(string)
    r = requests.post(ALGOLIA_URL, data=data)

    return r.json()['results'][0]['hits']


def search_comments(string):
    data = '''{"requests":[{"indexName":"test_comments","params":"query=%s&hitsPerPage=30&page=0"}]}''' % quote(string)
    r = requests.post(ALGOLIA_URL, data=data)

    return r.json()['results'][0]['hits']


def show_comment(comment):
    result = ('''<div style="border: 1px solid #B3B3B3; margin: 10px; padding: 10px;">comment by <a href="./users.php?userid=%s">%s</a>
        on <a href="./posts.php?id=%s">%s</a>
        · <a href="./posts.php?id=%s#%s">%s</a>
        · score: %s
        ''' % (comment['userId'],
               comment['authorUserName'],
               comment['postId'],
               htmlescape(comment['postTitle']),
               comment['postId'],
               comment['_id'],
               comment['postedAt'],
               comment['baseScore']))

    result += '''<pre style="font-family: Helvetica, sans-serif; word-wrap: break-word; white-space: pre-wrap; white-space: -moz-pre-wrap;">%s</pre>\n''' % htmlescape(comment['body'])
    result += "</div>"

    return result


def show_post(post, string, seen):
    result = ('''<div style="border: 1px solid #B3B3B3; margin: 10px; padding: 10px;"><a href="./posts.php?id=%s">%s</a>
    by <a href="./users.php?userid=%s">%s</a> · %s · score: %s
    ''' % (post['_id'],
           htmlescape(post['title']),
           post['userId'],
           post['authorUserName'],
           post['postedAt'],
           post['baseScore']))
    if string.lower() in post['body'].lower():
        result += '''<pre style="font-family: Helvetica, sans-serif; word-wrap: break-word; white-space: pre-wrap; white-space: -moz-pre-wrap;">%s</pre>\n''' % htmlescape(post['body'])
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
        print(show_comment(comment))

def print_posts(string):
    seen = set()
    for post in search_posts(string):
        print(show_post(post, string, seen))


if len(sys.argv) > 2:
    search_string = sys.argv[2]
    print(''' <!DOCTYPE html>
        <html>''')
    print(show_head(search_string))
    print("<body>")
    print(show_navbar())
    print('''<ul>
                <li><a href="#posts">Jump to post results</a></li>
                <li><a href="#comments">Jump to comment results</a></li>
            </ul>''')
    print('''<h2 id="posts">Post results</h2>''')
    print_posts(search_string)
    print('''<h2 id="comments">Comment results</h2>''')
    print_comments(search_string)
    print('''</body>
        </html>''')
