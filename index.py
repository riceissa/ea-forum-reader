#!/usr/bin/env python3

import sys
import datetime
from urllib.parse import quote

import config
import util
import linkpath


def posts_list_query(view="new", offset=0, before="", after="", run_query=True):
    query = ("""
    {
      posts(input: {
        terms: {
          view: "%s"
          limit: 50
          meta: null  # this seems to get both meta and non-meta posts
          %s
          %s
          %s
        }
      }) {
        results {
          _id
          title
          slug
          pageUrl
          postedAt
          baseScore
          voteCount
          commentCount
          meta
          question
          url
          user {
            username
            slug
            displayName
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
        return query + ('''\n<a href="%s">Run this query</a>\n\n''' % (config.GRAPHQL_URL.replace("graphql", "graphiql") + "?query=" + quote(query)))

    request = util.send_query(query)
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
            slug
          }
          user {
            _id
            slug
            username
            displayName
          }
          htmlBody
          postId
          pageUrl
        }
      }
    }
    """)

    if not run_query:
        return query + ('''\n<a href="%s">Run this query</a>\n\n''' % (config.GRAPHQL_URL.replace("graphql", "graphiql") + "?query=" + quote(query)))

    request = util.send_query(query)
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
    result += util.show_head(config.TITLE)
    result += "<body>\n"
    result += util.show_navbar(navlinks=[
        '''<a href="/?view=%s&amp;offset=%s&amp;before=%s&amp;after=%s&amp;format=queries" title="Show all the GraphQL queries used to generate this page">Queries</a>''' % (view, offset, before, after)
        ])
    result += '''<div id="wrapper">'''
    result += '''<div id="content">'''
    result += """<h1><a href="/">%s</a></h1>""" % config.TITLE

    result += '''
        View:
        <a href="/?view=new">New</a> ·
        <a href="/?view=old">Old</a> ·
        <a href="/?view=top">Top</a>
        <br /><br />
    '''

    if view == "top":
        result += ('''
            Restrict date range:
            <a href="/?view=top&amp;after=%s">Today</a> ·
            <a href="/?view=top&amp;after=%s">This week</a> ·
            <a href="/?view=top&amp;after=%s">This month</a> ·
            <a href="/?view=top&amp;after=%s">Last three months</a> ·
            <a href="/?view=top&amp;after=%s">This year</a> ·
            <a href="/?view=top">All time</a>
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
        result += '''<a href="/?view=%s&amp;offset=%s%s">← previous page (newer posts)</a> · ''' % (view, offset - 50, date_range_params)

    result += '''<a href="/?view=%s&amp;offset=%s%s">next page (older posts) →</a>''' % (view, offset + 50, date_range_params)
    result += '''<br/><br/>\n'''

    for post in posts:
        post_url = linkpath.posts(postid=post['_id'], postslug=post['slug'])
        result += ('''<div style="margin-bottom: 15px;">\n''')

        if "lesswrong" in config.GRAPHQL_URL:
            result += "[meta] " if post['meta'] else ""
        else:
            result += "[community] " if post['meta'] else ""
        if "question" in post and post["question"]:
            result += "[question] "
        if "url" in post and post["url"]:
            result += '''[<a href="%s">link</a>] ''' % post["url"]

        result += (('''    <a href="%s">''' % post_url) +
                   util.htmlescape(post['title']) + "</a><br />\n")

        result += util.userlink(slug=util.safe_get(post, ['user', 'slug']),
                                username=util.safe_get(post, ['user', 'username']),
                                display_name=util.safe_get(post, ['user', 'displayName']))
        result += " ·\n"
        result += post['postedAt'] + " ·\n"
        if util.safe_get(post, "question"):
            result += ('''    <a href="%s#answers">answers+comments (%s)</a>\n''' % (post_url, post['commentCount']))
        else:
            result += ('''    <a href="%s#comments">comments (%s)</a>\n''' % (post_url, post['commentCount']))
        result += ("</div>")

    if offset - 50 >= 0:
        result += '''<a href="/?view=%s&amp;offset=%s%s">← previous page (newer posts)</a> · ''' % (view, offset - 50, date_range_params)

    result += '''<a href="/?view=%s&amp;offset=%s%s">next page (older posts) →</a>''' % (view, offset + 50, date_range_params)

    result += """</div>"""
    result += '''
        <div id="sidebar">
            <h2>Archive</h2>
            <ul>
    '''
    start_year = 2006 if "lesswrong" in config.GRAPHQL_URL else 2011
    for year in range(start_year, datetime.datetime.utcnow().year + 1):
        result += "<li>\n"
        result += '''<a href="/?view=%s&amp;before=%s&amp;after=%s">%s</a>''' % (
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
                result += '''<li><a href="/?view=%s&amp;before=%s&amp;after=%s">%s</a></li>''' % (
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
        post = comment['post']
        if post is None:
            post = {'slug': util.safe_get(comment, 'pageUrl', default="").split('/')[-1].split('#')[0], 'title': '[deleted]'}
        result += ('''
            <a href="%s">%s</a> on <a href="%s#%s">%s</a><br/>
            <span style="font-size: 14px;">
            %s
            </span>
        ''' % (
                linkpath.users(userslug=util.safe_get(comment, ['user', 'slug'], "")),
                util.safe_get(comment, ['user', 'slug'], ""),
                linkpath.posts(postid=util.safe_get(comment, 'postId', default=""), postslug=post['slug']),
                comment['_id'],
                util.htmlescape(post['title']),
                util.substitute_alt_links(comment['htmlBody'])
            )
        )

    result += "</div>"  # sidebar
    result += """
    </div>
        </body>
    </html>
    """

    return result


if __name__ == "__main__":
    if len(sys.argv) != 5+1:
        print("Unexpected number of arguments")
    else:
        print(show_daily_posts(offset=int(sys.argv[1]), view=sys.argv[2],
                               before=sys.argv[3], after=sys.argv[4],
                               display_format=sys.argv[5]))
