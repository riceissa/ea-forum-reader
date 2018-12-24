#!/usr/bin/env python3

import sys
from urllib.parse import quote

import util
import config
import linkpath


def html_page_for_user(username, display_format):
    run_query = False if display_format == "queries" else True
    comments = get_comments_for_user(username, run_query=run_query)
    posts = get_posts_for_user(username, run_query=run_query)
    user_info = query_user_info(username, run_query=run_query)

    if display_format == "queries":
        result = "<pre>"
        result += comments + "\n"
        result += posts + "\n"
        result += user_info + "\n"
        result += "</pre>\n"
        return result

    result = """<!DOCTYPE html>
    <html>
    """
    result += util.show_head(username)
    result += "<body>"
    feed_link = '''<a href="%s">Feed</a>''' % linkpath.users(userslug=username, display_format="rss")
    result += util.show_navbar(navlinks=[
            feed_link,
            '''<a href="%s" title="Show all the GraphQL queries used to generate this page">Queries</a>''' % linkpath.users(userslug=util.htmlescape(username), display_format="queries")
        ])
    result += '''<div id="wrapper">'''

    result += '''<div id="sidebar">'''
    result += '''<h2>User info</h2>'''
    result += '''  <dl>'''
    if "displayName" in user_info and user_info["displayName"]:
        result += '''    <dt>Display name</dt>'''
        result += '''    <dd>%s</dd>''' % user_info["displayName"]
    if "karma" in user_info and user_info["karma"]:
        result += '''    <dt>Karma</dt>'''
        result += '''    <dd>%s</dd>''' % user_info["karma"]
    if "location" in user_info and user_info["location"]:
        result += '''    <dt>Location</dt>'''
        result += '''    <dd>%s</dd>''' % user_info["location"]
    if "htmlBio" in user_info and user_info["htmlBio"]:
        result += '''    <dt>Biography</dt>'''
        result += '''    <dd>%s</dd>''' % user_info["htmlBio"]
    if "postCount" in user_info and user_info["postCount"]:
        result += '''    <dt>Post count</dt>'''
        result += '''    <dd>%s</dd>''' % user_info["postCount"]
    if "commentCount" in user_info and user_info["commentCount"]:
        result += '''    <dt>Comment count</dt>'''
        result += '''    <dd>%s</dd>''' % user_info["commentCount"]
    if "website" in user_info and user_info["website"]:
        result += '''    <dt>Website</dt>'''
        result += '''    <dd><a href="%s">%s</a></dd>''' % (user_info["website"],
                                                            user_info["website"])
    result += '''  </dl>'''
    result += '''</div>'''  # closes sidebar

    result += '''<div id="content">'''

    all_content = []
    all_content.extend(comments)
    all_content.extend(posts)
    all_content = sorted(all_content, key=lambda x: x['postedAt'], reverse=True)

    for content in all_content:
        content_type = "post" if "title" in content else "comment"
        result += '''<div style="border: 1px solid #B3B3B3; margin-bottom: 15px; padding: 10px; background-color: %s;">\n''' % config.COMMENT_COLOR
        if content_type == "post":
            result += '''    <h2><a href="%s">%s</a></h2>\n''' % (linkpath.posts(postid=content['_id'], postslug=content['slug']), util.htmlescape(content['title']))
            result += '''    %s · score: %s (%s votes)\n''' % (content['postedAt'], content['baseScore'], content['voteCount'])
        else:
            if content['post'] is None:
                postslug = content['pageUrl'].split('/')[-1].split('#')[0]
                result += '''    <a href="%s#%s">Comment</a> by <b>%s</b> on [deleted post]</b>\n''' % (linkpath.posts(postid=content['postId'], postslug=postslug), content['_id'], content['user']['username'])
                result += '''    %s\n''' % content['postedAt']
            else:
                if "lesswrong" in config.GRAPHQL_URL:
                    official_link = '''<a href="%s" title="Official LessWrong 2.0 link">LW</a>''' % content['pageUrl']
                else:
                    official_link = '''<a href="%s" title="Official EA Forum link">EA</a>''' % content['pageUrl']
                result += ('''    Comment by
                    <b>%s</b> on
                    <a href="%s">%s</a></b> ·
                    <a href="%s#%s">%s</a> ·
                    score: %s (%s votes) ·
                    %s ·
                    <a href="%s" title="GreaterWrong link">GW</a>''' % (
                        username,
                        linkpath.posts(postid=content['postId'], postslug=content['post']['slug']),
                        util.htmlescape(content['post']['title']),
                        linkpath.posts(postid=content['postId'], postslug=content['post']['slug']),
                        content['_id'],
                        content['postedAt'],
                        content['baseScore'],
                        content['voteCount'],
                        official_link,
                        util.ea_forum_to_gw(content['pageUrl'])))
            content_body = util.cleanHtmlBody(content['htmlBody'])
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
                result += "    <title>Comment by %s on %s</title>\n" % (content['user']['username'], util.htmlescape(content['post']['title']))
        result += '''    <link>%s</link>\n''' % content['pageUrl']
        content_body = util.htmlescape(util.cleanHtmlBody(content['htmlBody']))
        result += '''    <description>%s</description>\n''' % content_body
        result += '''    <author>%s</author>\n''' % username
        result += '''    <guid>%s</guid>\n''' % content['_id']
        result += '''    <pubDate>%s</pubDate>\n''' % content['postedAt']
        result += "</item>\n"

    result += '''</channel>
    </rss>'''

    return result


def query_user_info(userslug, run_query=True):
    query = ("""
    {
      user(input: {selector: {slug: "%s"}}) {
        result {
          _id
          slug
          karma
          htmlBio
          website
          location
          profile
          displayName
          username
          postCount
          commentCount
        }
      }
    }
    """ % userslug)

    if not run_query:
        query_url = config.GRAPHQL_URL.replace("graphql", "graphiql") + "?query=" + quote(query)
        return query + ('''\n<a href="%s">Run this query</a>\n\n''' % query_url)

    request = util.send_query(query)
    return request.json()['data']['user']['result']


def get_comments_for_user(username, run_query=True):
    userid = util.userslug_to_userid(username, run_query=True)
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
            displayName
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
        return util.userslug_to_userid(username, run_query=False) + "\n\n" + query + ('''\n<a href="%s">Run this query</a>\n\n''' % (config.GRAPHQL_URL.replace("graphql", "graphiql") + "?query=" + quote(query)))

    request = util.send_query(query)
    result = []
    for comment in request.json()['data']['comments']['results']:
        result.append(comment)
    return result


def get_posts_for_user(username, run_query=True):
    userid = util.userslug_to_userid(username, run_query=True)
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
        return util.userslug_to_userid(username, run_query=False) + "\n\n" + query + ('''\n<a href="%s">Run this query</a>\n\n''' % (config.GRAPHQL_URL.replace("graphql", "graphiql") + "?query=" + quote(query)))

    request = util.send_query(query)
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
