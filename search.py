#!/usr/bin/env python3

import sys
import json
import requests
from urllib.parse import quote

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
    result = ('''<div style="border: 1px solid black;">Comment by <a href="./users.php?userid=%s">%s</a>
        on <a href="./posts.php?id=%s">%s</a>
        ''' % (comment['userId'], comment['authorUserName'], comment['postId'], comment['postTitle']))

    result += '''<pre style="font-family: Helvetica, sans-serif; word-wrap: break-word; white-space: pre-wrap; white-space: -moz-pre-wrap;">%s</pre>\n''' % comment['body']
    result += "</div>"

    return result


def show_post(post):
    result = ('''<div style="border: 1px solid black;"><a href="./posts.php?id=%s">%s</a>
    ''' % (post['_id'], post['title']))
    result += '''<pre style="font-family: Helvetica, sans-serif; word-wrap: break-word; white-space: pre-wrap; white-space: -moz-pre-wrap;">%s</pre>\n''' % post['body']

    result += "</div>\n"
    return result

def print_comments(string):
    for comment in search_comments(string):
        print(show_comment(comment))

def print_posts(string):
    for post in search_posts(string):
        print(show_post(post))


# print(json.dumps(search_posts("carl shulman"), indent=4))


if len(sys.argv) > 2:
    search_string = sys.argv[2]
    print('''
        <ul>
            <li><a href="#posts">Jump to post results</a></li>
            <li><a href="#comments">Jump to comment results</a></li>
        </ul>
    ''')
    print('''<h2 id="posts">Post results</h2>''')
    print_posts(search_string)
    print('''<h2 id="comments">Comment results</h2>''')
    print_comments(search_string)
