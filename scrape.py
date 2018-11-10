#!/usr/bin/env python3

import requests
import json
import sys

def send_query(query):
    return requests.get('https://forum.effectivealtruism.org/graphql', params={'query': query})

def cleanHtmlBody(htmlBody):
    """For some reason htmlBody values often have the following tags that
    really shouldn't be there."""
    return (htmlBody.replace("<html>", "")
                    .replace("</html>", "")
                    .replace("<body>", "")
                    .replace("</body>", "")
                    .replace("<head>", "")
                    .replace("</head>", ""))

def get_userid(username):
    query = ("""
    {
      user(input: {selector: {slug: "%s"}}) {
        result {
          _id
        }
      }
    }
    """ % username)

    request = send_query(query)

    return request.json()['data']['user']['result']['_id']

def get_content_for_post(postid):
    query = ("""
    {
      post(
        input: {
          selector: {
            _id: "%s"
          }
        }
      ) {
        result {
          _id
          createdAt
          postedAt
          url
          title
          slug
          body
          commentsCount
          htmlBody
          user {
            username
          }
        }
      }
    }
    """ % postid)

    request = send_query(query)
    return request.json()['data']['post']['result']

def get_comments_for_post(postid):
    query = ("""
    {
      comments(input: {
        terms: {
          view: "postCommentsTop",
          postId: "%s",
        }
      }) {
        results {
          _id
          user {
            _id
            username
            displayName
          }
          userId
          author
          parentCommentId
          pageUrl
          body
          htmlBody
          baseScore
          voteCount
          postedAt
        }
      }
    }
    """ % postid)

    request = send_query(query)
    result = []
    for comment in request.json()['data']['comments']['results']:
        result.append(comment)

    return result


class CommentTree(object):
    def __init__(self, commentid, data):
        self.commentid = commentid
        self.data = data
        self.children = []
        self.parity = None

    def __repr__(self):
        return self.commentid + "[" + str(self.children) + "]"

    def insert(self, child):
        self.children.append(child)

def build_comment_thread(comments):
    # Convert comments to tree nodes
    nodes = []
    for comment in comments:
        nodes.append(CommentTree(commentid=comment['_id'], data=comment))

    # Build index to be able to find nodes by their IDs
    index = {}
    for node in nodes:
        index[node.commentid] = node

    root = CommentTree("root", {})

    for node in nodes:
        parent = node.data['parentCommentId']
        if not parent:
            root.insert(node)
        else:
            try:
                index[parent].insert(node)
            except KeyError:
                # For some reason, comments sometimes refer to non-existent
                # parents, e.g. on post xuQ4dCHBtRXFZG487 there is a parent
                # called rjgZaK8uzHG3jAu2p that many comments refer to, but
                # this parent doesn't exist (and never existed, if you look at
                # the original post)
                # https://web.archive.org/web/20160824012747/http://effective-altruism.com/ea/10l/june_2016_givewell_board_meeting/
                root.insert(node)

    update_parity(root, "even")

    return root

def update_parity(comment_node, parity):
    comment_node.parity = parity
    for child in comment_node.children:
        child_parity = "even" if parity == "odd" else "odd"
        update_parity(child, child_parity)


def print_comment(comment_node):
    result = ""
    comment = comment_node.data
    color = "#ECF5FF" if comment_node.parity == "odd" else "#FFFFFF"

    # If this is the root node, comment is {} so skip it
    if comment:
        commentid = comment['_id']
        result += ('''<div id="%s" style="border: 1px solid #B3B3B3; padding-left: 15px; padding-right: 0px; padding-bottom: 10px; padding-top: 10px; margin-left: 0px; margin-right: -1px; margin-bottom: 0px; margin-top: 10px; background-color: %s">''' % (commentid, color))
        user = comment['user']['username'] if comment['user'] else "[deleted]"
        result += ("comment by <b>" + user + "</b>, ")
        result += (('''<a href="#%s">''' % commentid) + comment['postedAt'] + "</a>, ")
        result += ("score: " + str(comment['baseScore']) + " (" + str(comment['voteCount']) + " votes), ")
        result += ('<a title="EA Forum link" href="' + comment['pageUrl'] + '">EA</a>')
        result += (cleanHtmlBody(comment['htmlBody']))

    if comment_node.children:
        for child in comment_node.children:
            result += print_comment(child)

    result += ("</div>")

    return result


def print_comment_thread(postid):
    comments = get_comments_for_post(postid)
    root = build_comment_thread(comments)
    return print_comment(root)

def print_post_and_comment_thread(postid):
    result = ""
    post = get_content_for_post(postid)

    result += ("""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
        <title>%s</title>
        <style type="text/css">
            body { font-family: Helvetica, sans-serif; }
        </style>
    </head>
    <body>
    """ % post['title'])

    result += ("<h1>" + post['title'] + "</h1>")
    result += ('post by <b>' + post['user']['username'] + '</b><br />')
    result += ('''<a href="#comments">''' + str(post['commentsCount']) + ' comments</a>')
    result += (cleanHtmlBody(post['htmlBody']))

    result += ('''<h2 id="comments">''' + str(post['commentsCount']) + ' comments</h2>')

    result += print_comment_thread(postid)

    result += ("""
        </body>
        </html>
    """)

    return result


def feed_for_user(username):
    result = '''<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title></title>
            <description></description>
            <language>en-us</language>
    '''

    comments = get_comments_for_user(username)
    posts = get_posts_for_user(username)

    all_content = []
    all_content.extend(comments)
    all_content.extend(posts)
    all_content = sorted(all_content, key=lambda x: x['postedAt'], reverse=True)

    for content in all_content:
        result += "<item>"
        result += "    <title>a</title>"
        result += '''    <link>%s</link>''' % content['pageUrl']
        content_body = content['htmlBody'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        result += '''    <description>%s</description>''' % content_body
        result += '''    <author>%s</author>''' % username
        result += '''    <guid>a</guid>'''
        result += "</item>"

    result += '''</channel>
    </rss>'''

    return result


def get_comments_for_user(username):
    userid = get_userid(username)
    query = ("""
    {
      comments(input: {
        terms: {
          view: "userComments",
          userId: "%s",
        }
      }) {
        results {
          userId
          body
          postedAt
          pageUrl
          htmlBody
        }
      }
    }
    """ % userid)

    request = send_query(query)
    result = []
    for comment in request.json()['data']['comments']['results']:
        result.append(comment)
    return result


def get_posts_for_user(username):
    userid = get_userid(username)
    query = ("""
    {
      posts(input: {
        terms: {
          view: "userPosts"
          userId: "%s"
          limit: 50
        }
      }) {
        results {
          pageUrl
          postedAt
          htmlBody
        }
      }
    }
    """ % userid)

    request = send_query(query)
    result = []
    for post in request.json()['data']['posts']['results']:
        result.append(post)
    return result

# if len(sys.argv) <= 1:
#     print("Please enter a post ID as argument")
# else:
#     print(print_post_and_comment_thread(sys.argv[1]))

print(feed_for_user("carl_shulman"))
