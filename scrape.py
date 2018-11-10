#!/usr/bin/env python3

import requests
import json
import pdb

def send_query(query):
    return requests.get('https://forum.effectivealtruism.org/graphql', params={'query': query})

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
          score
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

    return root


def print_comment(comment_node):
    comment = comment_node.data
    # pdb.set_trace()

    # If this is the root node, comment is {} so skip it
    if comment:
        print('''<div style="border: 1px solid black; padding: 5px; margin: 5px;">''')
        print("comment by <b>" + comment['user']['username'] + "</b>,")
        print("<a href=" + '"' + comment['pageUrl'] + '"' + ">" + comment['postedAt'] + "</a>,")
        print("score: " + str(comment['score']) + " (" + str(comment['voteCount']) + " votes)")
        print(comment['htmlBody'])

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
    print("<h1>" + post['title'] + "</h1>")
    print('post by <b>' + post['user']['username'] + '</b><br />')
    print('''<a href="#comments">''' + str(post['commentsCount']) + ' comments</a>')
    print(post['htmlBody'])

    print('''<h2 id="comments">''' + str(post['commentsCount']) + ' comments</h2>')

    print_comment_thread(postid)


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

print_post_and_comment_thread("NDszJWMsdLCB4MNoy")
