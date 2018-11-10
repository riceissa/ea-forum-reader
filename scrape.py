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
            index[parent].insert(node)

    update_parity(root, "even")

    return root

def update_parity(comment_node, parity):
    comment_node.parity = parity
    for child in comment_node.children:
        child_parity = "even" if parity == "odd" else "odd"
        update_parity(child, child_parity)


def print_comment(comment_node):
    comment = comment_node.data
    color = "#ECF5FF" if comment_node.parity == "odd" else "#FFFFFF"

    # If this is the root node, comment is {} so skip it
    if comment:
        commentid = comment['_id']
        print(f'''<div id="{commentid}" style="border: 1px solid #B3B3B3; padding: 10px; margin: 5px; background-color: {color}">''')
        print("comment by <b>" + comment['user']['username'] + "</b>,")
        print(f'''<a href="#{commentid}">''' + comment['postedAt'] + "</a>,")
        print("score: " + str(comment['baseScore']) + " (" + str(comment['voteCount']) + " votes),")
        print('<a title="EA Forum link" href="' + comment['pageUrl'] + '">EA</a>')
        print(cleanHtmlBody(comment['htmlBody']))

    if comment_node.children:
        for child in comment_node.children:
            print_comment(child)

    print("</div>")


def print_comment_thread(postid):
    comments = get_comments_for_post(postid)
    root = build_comment_thread(comments)
    print_comment(root)

def print_post_and_comment_thread(postid):
    post = get_content_for_post(postid)

    print("""<!DOCTYPE html>
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

    print("<h1>" + post['title'] + "</h1>")
    print('post by <b>' + post['user']['username'] + '</b><br />')
    print('''<a href="#comments">''' + str(post['commentsCount']) + ' comments</a>')
    print(cleanHtmlBody(post['htmlBody']))

    print('''<h2 id="comments">''' + str(post['commentsCount']) + ' comments</h2>')

    print_comment_thread(postid)

    print("""
        </body>
        </html>
    """)


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
        }
      }
    }
    """ % userid)

    request = send_query(query)
    result = []
    for post in request.json()['data']['posts']['results']:
        result.append(post['pageUrl'])
    return result

if len(sys.argv) <= 1:
    print("Please enter a post ID as argument")
else:
    print_post_and_comment_thread(sys.argv[1])
