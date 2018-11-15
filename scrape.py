#!/usr/bin/env python3

import requests
import datetime

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
            blockquote {
                border-left: 2px solid #369;
                padding-left: 10px;
                margin-right: 15px;
                margin-left: 0px;
            }
            h1 {
                color: #326492;
            }
            img {
                max-width: 100%%;
                height: auto;
            }
            table {
                background-color: #f9f9f9;
                border-collapse: collapse;
                border-bottom: none;
                border-top: none;
            }
            table th {
                background-color: #f2f2f2;
                border: 1px solid #aaaaaa;
                font-weight: bold;
                padding: 5px 10px;
            }
            table td {
                border: 1px solid #aaaaaa;
                padding: 5px 10px;
            }
            #wrapper {
              border-left: 1px solid #d2d2d2;
              border-right: 1px solid #d2d2d2;
              margin: 0 auto;
              width: 1024px;
              overflow: hidden;
              background-color: #fff;
            }
            #content {
              padding: 30px 0 0 32px;
              background-color: #fff;
              width: 710px;
              float: left;
            }
            #sidebar {
              padding: 30px 32px 0 0;
              background-color: #fff;
              width: 220px;
              float: right;
            }
        </style>
    </head>
    """ % htmlescape(title))

    return result


def show_navbar(navlinks=None, search_value=""):
    if navlinks is None:
        navlinks = []

    result = """<nav><a href=".">Home</a> ·
        <a href="https://github.com/riceissa/ea-forum-reader">About</a> ·
        <a href="./userlist.php">User list</a>
        """

    for link in navlinks:
        result += " · " + link

    if search_value:
        search_value = 'value="%s"' % htmlescape(search_value)

    result += ("""
        <form action="./search.php" method="get" style="display: inline-block;">
                <input name="q" type="text" %s/>
                <input type="submit" value="Search" />
        </form>
    </nav>
    """ % search_value)

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

def posts_list_query(view="new", offset=0, before="", after="", run_query=True):
    query = ("""
    {
      posts(input: {
        terms: {
          view: "%s"
          limit: 50
          %s
          %s
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
    """ % (
            view,
            "offset: " + str(offset) if offset > 0 else "",
            ('before: "%s"' % before) if before else "",
            ('after: "%s"' % after) if after else ""
        )
    )

    if not run_query:
        return query

    request = send_query(query)
    return request.json()['data']['posts']['results']


def recent_comments_query(run_query=True):
    query = ("""
    {
      comments(input: {
        terms: {
          view: "recentComments"
          limit: 10
        }
      }) {
        results {
          _id
          post {
            _id
            title
          }
          user {
            _id
            slug
          }
          plaintextExcerpt
          htmlHighlight
        }
      }
    }
    """)

    if not run_query:
        return query

    request = send_query(query)
    return request.json()['data']['comments']['results']

def show_daily_posts(offset, view, before, after, display_format):
    posts = posts_list_query(offset=offset, view=view, before=before, after=after,
                             run_query=(False if display_format == "queries" else True))
    recent_comments = recent_comments_query(run_query=(False if display_format == "queries" else True))

    if display_format == "queries":
        result = "<pre>"
        result += posts + "\n"  # this is just the query string
        result += recent_comments + "\n"
        result += "</pre>\n"

        return result


    result = """<!DOCTYPE html>
    <html>
    """
    result += show_head("EA Forum Reader")
    result += "<body>\n"
    result += show_navbar(navlinks=[
        '''<a href="./?view=%s&amp;offset=%s&amp;before=%s&amp;after=%s&amp;format=queries" title="Show all the GraphQL queries used to generate this page">Queries</a>''' % (view, offset, before, after)
        ])
    result += '''<div id="wrapper">'''
    result += '''
        <div id="sidebar">
            <h2>Archive</h2>
            <ul>
    '''
    for year in range(2011, datetime.datetime.utcnow().year + 1):
        result += "<li>\n"
        result += '''<a href="./?view=%s&amp;before=%s&amp;after=%s">%s</a>''' % (
            view,
            str(year) + "-12-31",
            str(year) + "-01-01",
            year
        )
        if str(year) == after[:4] and str(year) == before[:4]:
            # If we are here, it means we are viewing the "archive" for this
            # year (or a month within this year), so show the months in the
            # sidebar so that we can go inside the months.
            result += "<ul>"
            for month in range(1, 12 + 1):
                if month == 12:
                    last_day = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
                else:
                    last_day = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
                result += '''<li><a href="./?view=%s&amp;before=%s&amp;after=%s">%s</a></li>''' % (
                    view,
                    last_day.strftime("%Y-%m-%d"),
                    str(year) + "-" + str(month).zfill(2) + "-01",
                    datetime.date(2000, month, 1).strftime("%B")
                )
            result += "</ul>"
        result += "</li>\n"
    result += "</ul>"

    result += '''<h2>Recent comments</h2>'''
    for comment in recent_comments:
        result += ('''
            <a href="./users.php?id=%s">%s</a> on <a href="./posts.php?id=%s#%s">%s</a><br/>
            <span style="font-size: 14px;">
            %s
            </span>
        ''' % (
                comment['user']['slug'],
                comment['user']['slug'],
                comment['post']['_id'],
                comment['_id'],
                htmlescape(comment['post']['title']),
                comment['htmlHighlight']
            )
        )

    result += "</div>"  # sidebar
    result += '''<div id="content">'''
    result += """<h1><a href="./">EA Forum Reader</a></h1>"""

    result += '''
        View:
        <a href="./?view=new">New</a> ·
        <a href="./?view=old">Old</a> ·
        <a href="./?view=top">Top</a>
        <br /><br />
    '''

    if view == "top":
        result += ('''
            Restrict date range:
            <a href="./?view=top&amp;after=%s">Today</a> ·
            <a href="./?view=top&amp;after=%s">This week</a> ·
            <a href="./?view=top&amp;after=%s">This month</a> ·
            <a href="./?view=top&amp;after=%s">Last three months</a> ·
            <a href="./?view=top&amp;after=%s">This year</a> ·
            <a href="./?view=top">All time</a>
            <br />
            <br />
        ''' % (
                # Today's posts are all posts after yesterday's date
                (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
                # This week
                (datetime.datetime.utcnow() - datetime.timedelta(days=7)).strftime("%Y-%m-%d"),
                # This month
                (datetime.datetime.utcnow() - datetime.timedelta(days=30)).strftime("%Y-%m-%d"),
                # Last three months
                (datetime.datetime.utcnow() - datetime.timedelta(days=90)).strftime("%Y-%m-%d"),
                # This year
                (datetime.datetime.utcnow() - datetime.timedelta(days=365)).strftime("%Y-%m-%d"),
            )
        )

    date_range_params = ""
    if before:
        date_range_params += "&amp;before=%s" % before
    if after:
        date_range_params += "&amp;after=%s" % after

    if offset - 50 >= 0:
        result += '''<a href="./?view=%s&amp;offset=%s%s">← previous page (newer posts)</a> · ''' % (view, offset - 50, date_range_params)

    result += '''<a href="./?view=%s&amp;offset=%s%s">next page (older posts) →</a>''' % (view, offset + 50, date_range_params)
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
        result += '''<a href="./?view=%s&amp;offset=%s%s">← previous page (newer posts)</a> · ''' % (view, offset - 50, date_range_params)

    result += '''<a href="./?view=%s&amp;offset=%s%s">next page (older posts) →</a>''' % (view, offset + 50, date_range_params)

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


def userslug_to_userid(userslug, run_query=True):
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

    if not run_query:
        return query

    request = send_query(query)
    return request.json()['data']['user']['result']['_id']


def get_content_for_post(postid, run_query=True):
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

    if not run_query:
        return query

    request = send_query(query)
    return request.json()['data']['post']['result']

def get_comments_for_post(postid, run_query=True):
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

    if not run_query:
        return query

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
            result += '''comment by <b><a href="./users.php?id=%s">%s</a></b> ·\n''' % (comment['user']['slug'], comment['user']['username'])
        else:
            result += '''comment by <b>[deleted]</b> ·\n'''
        result += (('''<a href="#%s">''' % commentid) + comment['postedAt'] + "</a> · ")
        result += ("score: " + str(comment['baseScore']) + " (" + str(comment['voteCount']) + " votes) · ")
        result += ('<a title="EA Forum link" href="' + comment['pageUrl'] + '">EA</a> · ')
        result += '<a title="GreaterWrong link" href="' + ea_forum_to_gw(comment['pageUrl']) + '">GW</a>'
        result += (cleanHtmlBody(comment['htmlBody']))

    if comment_node.children:
        for child in comment_node.children:
            result += print_comment(child)

    result += ("</div>")

    return result


def print_post_and_comment_thread(postid, display_format):
    post = get_content_for_post(postid, run_query=(False if display_format == "queries" else True))
    comments = get_comments_for_post(postid, run_query=(False if display_format == "queries" else True))

    if display_format == "queries":
        result = "<pre>"
        result += post + "\n"
        result += comments + "\n"
        result += "</pre>\n"
        return result

    result = """<!DOCTYPE html>
    <html>
    """
    result += show_head(post['title'])
    result += "<body>\n"
    result += show_navbar(navlinks=[
            '''<a href="./posts.php?id=%s&amp;format=queries" title="Show all the GraphQL queries used to generate this page">Queries</a>''' % htmlescape(postid)
        ])
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

    root = build_comment_thread(comments)
    result += print_comment(root)

    result += ("""
    </div>
    </div>
        </body>
        </html>
    """)

    return result


def html_page_for_user(username, display_format):
    comments = get_comments_for_user(username, run_query=(False if display_format == "queries" else True))
    posts = get_posts_for_user(username, run_query=(False if display_format == "queries" else True))

    if display_format == "queries":
        result = "<pre>"
        result += comments + "\n"
        result += posts + "\n"
        result += "</pre>\n"
        return result

    result = """<!DOCTYPE html>
    <html>
    """
    result += show_head(username)
    result += "<body>"
    feed_link = '''<a href="./users.php?id=%s&format=rss">Feed</a>''' % username
    result += show_navbar(navlinks=[
            feed_link,
            '''<a href="./users.php?id=%s&amp;format=queries" title="Show all the GraphQL queries used to generate this page">Queries</a>''' % htmlescape(username)
        ])
    result += '''<div id="wrapper">'''
    result += '''<div id="content">'''

    all_content = []
    all_content.extend(comments)
    all_content.extend(posts)
    all_content = sorted(all_content, key=lambda x: x['postedAt'], reverse=True)

    for content in all_content:
        content_type = "post" if "title" in content else "comment"
        result += '''<div style="border: 1px solid #B3B3B3; margin-bottom: 15px; padding: 10px; background-color: #ECF5FF;">\n'''
        if content_type == "post":
            result += '''    <h2><a href="./posts.php?id=%s">%s</a></h2>\n''' % (content['_id'], htmlescape(content['title']))
            result += '''    %s · score: %s (%s votes)\n''' % (content['postedAt'], content['baseScore'], content['voteCount'])
        else:
            if content['post'] is None:
                result += '''    <a href="./posts.php?id=%s#%s">Comment</a> by <b>%s</b> on [deleted post]</b>\n''' % (content['postId'], content['_id'], content['user']['username'])
                result += '''    %s\n''' % content['postedAt']
            else:
                result += ('''    Comment by
                    <b>%s</b> on
                    <a href="./posts.php?id=%s">%s</a></b> ·
                    <a href="./posts.php?id=%s#%s">%s</a> ·
                    score: %s (%s votes) ·
                    <a href="%s" title="EA Forum link">EA</a> ·
                    <a href="%s" title="GreaterWrong link">GW</a>''' % (
                        username,
                        content['postId'],
                        htmlescape(content['post']['title']),
                        content['postId'],
                        content['_id'],
                        content['postedAt'],
                        content['baseScore'],
                        content['voteCount'],
                        content['pageUrl'],
                        ea_forum_to_gw(content['pageUrl'])))
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


def get_comments_for_user(username, run_query=True):
    userid = userslug_to_userid(username, run_query=True)
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
          baseScore
          voteCount
        }
      }
    }
    """ % userid)

    if not run_query:
        return userslug_to_userid(username, run_query=False) + "\n\n" + query

    request = send_query(query)
    result = []
    for comment in request.json()['data']['comments']['results']:
        result.append(comment)
    return result


def get_posts_for_user(username, run_query=True):
    userid = userslug_to_userid(username, run_query=True)
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
          voteCount
          baseScore
        }
      }
    }
    """ % userid)

    if not run_query:
        return userslug_to_userid(username, run_query=False) + "\n\n" + query

    request = send_query(query)
    result = []
    for post in request.json()['data']['posts']['results']:
        result.append(post)
    return result
