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
    user_info_and_status_code = query_user_info(username, run_query=run_query)
    if isinstance(user_info_and_status_code, str):
        user_info = user_info_and_status_code
    else:
        user_info, status_code = user_info_and_status_code
        if status_code != 200:
            return util.error_message_string("users", username, status_code)

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
    result += '<p>'
    if "lesswrong" in config.GRAPHQL_URL:
        result += ('<a title="Official LessWrong 2.0 link" href="https://www.lesswrong.com/users/' + username + '">LW</a> · ')
        result += ('<a title="GreaterWrong link" href="https://www.greaterwrong.com/users/' + username + '">GW</a>')
    else:
        result += ('<a title="Official EA Forum link" href="https://forum.effectivealtruism.org/users/' + username + '">EA</a> · ')
        result += ('<a title="GreaterWrong link" href="https://ea.greaterwrong.com/users/' + username + '">GW</a>')
    result += '</p>'
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

    result += '''
        <ul>
            <li><a href="#posts">Posts</a></li>
            <li><a href="#comments">Comments</a></li>
        </ul>
    '''

    result += '''<h2 id="posts">Posts</h2>'''
    for post in posts:
        result += '''<div style="border: 1px solid #B3B3B3; margin-bottom: 15px; padding: 10px; background-color: %s;">\n''' % config.COMMENT_COLOR
        result += '''    <a href="%s">%s</a>\n''' % (linkpath.posts(postid=util.safe_get(post, '_id'), postslug=util.safe_get(post, 'slug')), util.htmlescape(util.safe_get(post, 'title')))
        result += '''    %s\n''' % (util.safe_get(post, 'postedAt'))
        result += "</div>\n"

    result += '''<h2 id="comments">Comments</h2>'''
    for comment in comments:
        result += '''<div style="border: 1px solid #B3B3B3; margin-bottom: 15px; padding: 10px; background-color: %s;">\n''' % config.COMMENT_COLOR
        if comment['post'] is None:
            postslug = util.safe_get(comment, 'pageUrl', default="").split('/')[-1].split('#')[0]
            result += '''    <a href="%s#%s">Comment</a> by <b>%s</b> on [deleted post]</b>\n''' % (linkpath.posts(postid=comment['postId'], postslug=postslug), util.safe_get(comment, '_id'), util.safe_get(comment, ['user', 'username']))
            result += '''    %s\n''' % comment['postedAt']
        else:
            if "lesswrong" in config.GRAPHQL_URL:
                official_link = '''<a href="%s" title="Official LessWrong 2.0 link">LW</a>''' % comment['pageUrl']
            else:
                official_link = '''<a href="%s" title="Official EA Forum link">EA</a>''' % comment['pageUrl']
            result += ('''    Comment by
                <b>%s</b> on
                <a href="%s">%s</a></b> ·
                <a href="%s#%s">%s</a> ·
                %s ·
                <a href="%s" title="GreaterWrong link">GW</a>''' % (
                    util.userlink(slug=util.safe_get(user_info, 'slug'),
                                  username=util.safe_get(user_info, 'username'),
                                  display_name=util.safe_get(user_info, 'displayName')),
                    linkpath.posts(postid=comment['postId'], postslug=util.safe_get(comment, ['post', 'slug'])),
                    util.htmlescape(comment['post']['title']),
                    linkpath.posts(postid=comment['postId'], postslug=util.safe_get(comment, ['post', 'slug'])),
                    comment['_id'],
                    comment['postedAt'],
                    official_link,
                    util.official_url_to_gw(comment['pageUrl'])))
        comment_body = util.cleanHtmlBody(comment['htmlBody'])
        result += '''    %s\n''' % comment_body
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
        result += '''    <link>%s</link>\n''' % util.official_url_to_reader(content['pageUrl'])
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

    request = util.send_query(query, operation_name="query_user_info")
    return util.get_from_request(request, ['data', 'user', 'result'])


def get_comments_for_user(username, run_query=True):
    userid_and_status_code = util.userslug_to_userid(username, run_query=True)
    if isinstance(userid_and_status_code, str):
        userid = userid_and_status_code
    else:
        userid, status_code = userid_and_status_code
        if status_code != 200:
            return util.error_message_string("users", username, status_code)
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
        r_and_status_code = util.userslug_to_userid(username, run_query=False)
        assert isinstance(r_and_status_code, str)
        r = r_and_status_code
        return r + "\n\n" + query + ('''\n<a href="%s">Run this query</a>\n\n''' % (config.GRAPHQL_URL.replace("graphql", "graphiql") + "?query=" + quote(query)))

    request = util.send_query(query, operation_name="get_comments_for_user")
    result = []
    comments_and_status_code = util.get_from_request(request, ['data', 'comments', 'results'])
    if isinstance(comments_and_status_code, str):
        comments = comments_and_status_code
    else:
        comments, status_code = comments_and_status_code
        if status_code != 200:
            return f"Received status code of {status_code} from API endpoint."
    for comment in comments:
        result.append(comment)
    return result


def get_posts_for_user(username, run_query=True):
    userid, status_code = util.userslug_to_userid(username, run_query=True)
    if status_code != 200:
        return f"Received status code of {status_code} from API endpoint."
    query = ("""
    {
      posts(input: {
        terms: {
          view: "userPosts"
          userId: "%s"
          limit: 50
          meta: null  # this seems to get both meta and non-meta posts
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
        r_and_status_code = util.userslug_to_userid(username, run_query=False)
        assert isinstance(r_and_status_code, str)
        r = r_and_status_code
        return r + "\n\n" + query + ('''\n<a href="%s">Run this query</a>\n\n''' % (config.GRAPHQL_URL.replace("graphql", "graphiql") + "?query=" + quote(query)))

    request = util.send_query(query, operation_name="get_posts_for_user")
    result = []
    posts, status_code = util.get_from_request(request, ['data', 'posts', 'results'])
    if status_code != 200:
        return f"Received status code of {status_code} from API endpoint."
    for post in posts:
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
