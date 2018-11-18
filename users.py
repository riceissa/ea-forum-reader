#!/usr/bin/env python3

import sys
from scrape import *

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
    feed_link = '''<a href="%s">Feed</a>''' % linkpath.users(userslug=username, display_format="rss")
    result += show_navbar(navlinks=[
            feed_link,
            '''<a href="%s" title="Show all the GraphQL queries used to generate this page">Queries</a>''' % linkpath.users(userslug=htmlescape(username), display_format="queries")
        ])
    result += '''<div id="wrapper">'''
    result += '''<div id="content">'''

    all_content = []
    all_content.extend(comments)
    all_content.extend(posts)
    all_content = sorted(all_content, key=lambda x: x['postedAt'], reverse=True)

    for content in all_content:
        content_type = "post" if "title" in content else "comment"
        result += '''<div style="border: 1px solid #B3B3B3; margin-bottom: 15px; padding: 10px; background-color: %s;">\n''' % config.COMMENT_COLOR
        if content_type == "post":
            result += '''    <h2><a href="%s">%s</a></h2>\n''' % (linkpath.posts(postid=content['_id'], postslug=content['slug']), htmlescape(content['title']))
            result += '''    %s · score: %s (%s votes)\n''' % (content['postedAt'], content['baseScore'], content['voteCount'])
        else:
            if content['post'] is None:
                postslug = content['pageUrl'].split('/')[-1].split('#')[0]
                result += '''    <a href="%s#%s">Comment</a> by <b>%s</b> on [deleted post]</b>\n''' % (linkpath.posts(postid=content['postId'], postslug=postslug), content['_id'], content['user']['username'])
                result += '''    %s\n''' % content['postedAt']
            else:
                result += ('''    Comment by
                    <b>%s</b> on
                    <a href="%s">%s</a></b> ·
                    <a href="%s#%s">%s</a> ·
                    score: %s (%s votes) ·
                    <a href="%s" title="Official link">EA</a> ·
                    <a href="%s" title="GreaterWrong link">GW</a>''' % (
                        username,
                        linkpath.posts(postid=content['postId'], postslug=content['post']['slug']),
                        htmlescape(content['post']['title']),
                        linkpath.posts(postid=content['postId'], postslug=content['post']['slug']),
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
            <language>en-us</language>\n''' % (username + " feed - " + config.TITLE, username + "’s posts and comments on the Effective Altruism Forum"))

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
            slug
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
        return userslug_to_userid(username, run_query=False) + "\n\n" + query + ('''\n<a href="%s">Run this query</a>\n\n''' % (config.GRAPHQL_URL.replace("graphql", "graphiql") + "?query=" + quote(query)))

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
          slug
        }
      }
    }
    """ % userid)

    if not run_query:
        return userslug_to_userid(username, run_query=False) + "\n\n" + query + ('''\n<a href="%s">Run this query</a>\n\n''' % (config.GRAPHQL_URL.replace("graphql", "graphiql") + "?query=" + quote(query)))

    request = send_query(query)
    result = []
    for post in request.json()['data']['posts']['results']:
        result.append(post)
    return result

if __name__ == "__main__":
    if len(sys.argv) != 2 + 1:
        print("Unexpected number of arguments")
    else:
        if sys.argv[2] == "rss":
            print(feed_for_user(sys.argv[1]))
        else:
            print(html_page_for_user(username=sys.argv[1], display_format=sys.argv[2]))
