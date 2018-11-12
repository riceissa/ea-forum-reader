#!/usr/bin/env python3

import requests
import json

def htmlescape(string):
    return string.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def ea_forum_to_gw(ea_forum_link):
    return ea_forum_link.replace('forum.effectivealtruism.org', 'ea.greaterwrong.com', 1)

def show_head(title):
    result = ("""
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
        <title>%s</title>
        <style type="text/css">
            body {
                font-family: Lato, Helvetica, sans-serif;
                font-size: 16px;
                line-height: 1.4;
                background-color: whitesmoke;
            }
            a {
                color: #326492;
                text-decoration: underline;
            }
                a:visited {
                color: #8a8a8b;
            }
            h1 {
                color: #326492;
            }
            #wrapper {
              margin: 0 auto;
              width: 1024px;
              text-align: left;
              font-size: 14px;
              border-left: 1px solid #d2d2d2;
              border-right: 1px solid #d2d2d2;
              background-color: #fff;
            }
            #content {
              /* float: left; */
              padding: 30px 0 0 32px;
              width: 710px;
              clear: both;
              background-color: #fff;
            }
        </style>
    </head>
    """ % htmlescape(title))

    return result


def show_navbar(navlinks=None):
    if navlinks is None:
        navlinks = []

    result = """<nav><a href=".">Home</a> ·
        <a href="https://github.com/riceissa/ea-forum-reader">About</a>"""

    for link in navlinks:
        result += " · " + link

    result += """
        <form action="./search.php" method="get" style="display: inline-block;">
                <input name="q" type="text" />
                <input type="submit" value="Search" />
        </form>
    </nav>
    """

    return result

def send_query(query):
    return requests.get('https://forum.effectivealtruism.org/graphql', params={'query': query})

def cleanHtmlBody(htmlBody):
    """For some reason htmlBody values often have the following tags that
    really shouldn't be there."""
    if htmlBody is None:
        return ""
    return (htmlBody.replace("<html>", "")
                    .replace("</html>", "")
                    .replace("<body>", "")
                    .replace("</body>", "")
                    .replace("<head>", "")
                    .replace("</head>", ""))

def get_daily_posts(offset=0):
    query = ("""
    {
      posts(input: {
        terms: {
          view: "new"
          limit: 50
          %s
        }
      }) {
        results {
          _id
          title
          pageUrl
          postedAt
          baseScore
          voteCount
          commentsCount
          user {
            username
            slug
          }
        }
      }
    }
    """ % ("" if offset == 0 else "offset: " + str(offset)))
    request = send_query(query)
    return request.json()['data']['posts']['results']

def show_daily_posts(offset=0):
    posts = get_daily_posts(offset)

    result = """<!DOCTYPE html>
    <html>
    """
    result += show_head("EA Forum Reader")
    result += "<body>\n"
    result += show_navbar()
    result += '''<div id="wrapper">'''
    result += '''<div id="content">'''
    result += """<h1>EA Forum Reader</h1>"""

    if offset - 50 >= 0:
        result += '''<a href="./index.php?offset=%s">← previous page (newer posts)</a> · ''' % (offset - 50)

    result += '''<a href="./index.php?offset=%s">next page (older posts) →</a>''' % (offset + 50)
    result += '''<br/><br/>\n'''

    for post in posts:
        post_url = "./posts.php?id=" + post['_id']
        result += ('''<div style="margin-bottom: 15px;">\n''')
        result += (('''    <a href="%s">''' % post_url) + htmlescape(post['title']) + "</a><br />\n")
        if post['user'] is None:
            result += '''[deleted] ·\n'''
        else:
            result += '''<a href="./users.php?id=%s">%s</a> ·\n''' % (post['user']['slug'], post['user']['username'])
        result += post['postedAt'] + " ·\n"
        result += '''score: %s (%s votes) ·\n''' % (post['baseScore'], post['voteCount'])
        result += ('''    <a href="%s#comments">comments (%s)</a>\n''' % (post_url, post['commentsCount']))
        result += ("</div>")

    if offset - 50 >= 0:
        result += '''<a href="./index.php?offset=%s">← previous page (newer posts)</a> · ''' % (offset - 50)

    result += '''<a href="./index.php?offset=%s">next page (older posts) →</a>''' % (offset + 50)
    result += '''<br/><br/>\n'''

    result += """
    </div>
    </div>
        </body>
    </html>
    """

    return result


def userid_to_userslug(userid):
    query = ("""
    {
      user(input: {selector: {documentId: "%s"}}) {
        result {
          _id
          slug
        }
      }
    }
    """ % userid)

    request = send_query(query)
    return request.json()['data']['user']['result']['slug']


def userslug_to_userid(userslug):
    query = ("""
    {
      user(input: {selector: {slug: "%s"}}) {
        result {
          _id
          slug
        }
      }
    }
    """ % userslug)

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
          postedAt
          url
          title
          slug
          body
          commentsCount
          htmlBody
          baseScore
          voteCount
          pageUrl
          user {
            username
            slug
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
            slug
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
        if comment['user']:
            result += '''comment by <b><a href="./users.php?id=%s">%s</a></b>,\n''' % (comment['user']['slug'], comment['user']['username'])
        else:
            result += '''comment by <b>[deleted]</b>,\n'''
        result += (('''<a href="#%s">''' % commentid) + comment['postedAt'] + "</a> · ")
        result += ("score: " + str(comment['baseScore']) + " (" + str(comment['voteCount']) + " votes), ")
        result += ('<a title="EA Forum link" href="' + comment['pageUrl'] + '">EA</a> ·')
        result += '<a title="GreaterWrong link" href="' + ea_forum_to_gw(comment['pageUrl']) + '">GW</a>'
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

    result += """<!DOCTYPE html>
    <html>
    """
    result += show_head(post['title'])
    result += "<body>\n"
    result += show_navbar()
    result += '''<div id="wrapper">'''
    result += '''<div id="content">'''
    result += "<h1>" + htmlescape(post['title']) + "</h1>\n"
    result += '''post by <b><a href="./users.php?id=%s">%s</a></b> ·\n''' % (post['user']['slug'], post['user']['username'])
    result += '''%s ·\n''' % post['postedAt']
    result += '''score: %s (%s votes) ·\n''' % (post['baseScore'], post['voteCount'])
    result += '''<a href="%s" title="EA Forum link">EA</a> ·\n''' % post['pageUrl']
    result += '''<a href="%s" title="GreaterWrong link">GW</a> ·\n''' % ea_forum_to_gw(post['pageUrl'])
    result += '''<a href="#comments">''' + str(post['commentsCount']) + ' comments</a>\n'
    result += cleanHtmlBody(post['htmlBody'])

    result += '''<h2 id="comments">''' + str(post['commentsCount']) + ' comments</h2>'

    result += print_comment_thread(postid)

    result += ("""
    </div>
    </div>
        </body>
        </html>
    """)

    return result


def html_page_for_user(username):
    result = """<!DOCTYPE html>
    <html>
    """
    result += show_head(username)
    result += "<body>"
    feed_link = '''<a href="./users.php?id=%s&format=rss">Feed</a>''' % username
    result += show_navbar(navlinks=[feed_link])
    result += '''<div id="wrapper">'''
    result += '''<div id="content">'''
    comments = get_comments_for_user(username)
    posts = get_posts_for_user(username)

    all_content = []
    all_content.extend(comments)
    all_content.extend(posts)
    all_content = sorted(all_content, key=lambda x: x['postedAt'], reverse=True)

    for content in all_content:
        content_type = "post" if "title" in content else "comment"
        result += '''<div style="border: 1px solid #B3B3B3; margin-bottom: 15px; padding: 10px; background-color: #ECF5FF;">\n'''
        if content_type == "post":
            result += '''    <h2><a href="./posts.php?id=%s">%s</a></h2>\n''' % (content['_id'], htmlescape(content['title']))
            result += '''    %s\n''' % content['postedAt']
        else:
            if content['post'] is None:
                result += '''    <a href="./posts.php?id=%s#%s">Comment</a> by <b>%s</b> on [deleted post]</b>\n''' % (content['postId'], content['_id'], content['user']['username'])
            else:
                result += '''    <a href="./posts.php?id=%s#%s">Comment</a> by <b>%s</b> on <a href="./posts.php?id=%s">%s</a></b>,\n''' % (content['postId'], content['_id'], content['user']['username'], content['postId'], htmlescape(content['post']['title']))
            result += '''    %s\n''' % content['postedAt']
            content_body = cleanHtmlBody(content['htmlBody'])
            result += '''    %s\n''' % content_body
        result += "</div>\n"

    result += '''
        </div>
        </div>
        </body>
        </html>
    '''
    return result


def feed_for_user(username):
    result = ('''<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>%s</title>
            <description>%s</description>
            <language>en-us</language>\n''' % (username + " feed - EA Forum Reader", username + "’s posts and comments on the Effective Altruism Forum"))

    comments = get_comments_for_user(username)
    posts = get_posts_for_user(username)

    all_content = []
    all_content.extend(comments)
    all_content.extend(posts)
    all_content = sorted(all_content, key=lambda x: x['postedAt'], reverse=True)

    for content in all_content:
        content_type = "post" if "title" in content else "comment"
        result += "<item>\n"
        if content_type == "post":
            result += "    <title>%s</title>\n" % content['title']
        else:
            if content['post'] is None:
                result += "    <title>Comment by %s on [deleted post]</title>\n" % (content['user']['username'])
            else:
                result += "    <title>Comment by %s on %s</title>\n" % (content['user']['username'], htmlescape(content['post']['title']))
        result += '''    <link>%s</link>\n''' % content['pageUrl']
        content_body = htmlescape(cleanHtmlBody(content['htmlBody']))
        result += '''    <description>%s</description>\n''' % content_body
        result += '''    <author>%s</author>\n''' % username
        result += '''    <guid>%s</guid>\n''' % content['_id']
        result += '''    <pubDate>%s</pubDate>\n''' % content['postedAt']
        result += "</item>\n"

    result += '''</channel>
    </rss>'''

    return result


def get_comments_for_user(username):
    userid = userslug_to_userid(username)
    query = ("""
    {
      comments(input: {
        terms: {
          view: "userComments",
          userId: "%s",
          limit: 50,
        }
      }) {
        results {
          _id
          post {
            title
          }
          user {
            username
            slug
          }
          userId
          postId
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
    userid = userslug_to_userid(username)
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
          _id
          title
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
