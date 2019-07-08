#!/usr/bin/env python3

import sys
from urllib.parse import quote

import config
import util
import linkpath

def small_vote_power(karma):
    """See
    https://github.com/LessWrong2/Lesswrong2/blob/devel/packages/lesswrong/lib/modules/voting/new_vote_types.js
    for the vote power implementation. See also the blog post at
    https://lw2.issarice.com/posts/7Sx3CJXA7JHxY2yDG/strong-votes-update-deployed#Vote_Power_by_Karma"""
    if karma is None:
        return 1
    if karma >= 25000:
        return 3
    if karma >= 1000:
        return 2
    return 1


def big_vote_power(karma):
    """See
    https://github.com/LessWrong2/Lesswrong2/blob/devel/packages/lesswrong/lib/modules/voting/new_vote_types.js
    for the vote power implementation. See also the blog post at
    https://lw2.issarice.com/posts/7Sx3CJXA7JHxY2yDG/strong-votes-update-deployed#Vote_Power_by_Karma"""
    if karma is None:
        return 1
    if karma >= 500000:
        return 16
    if karma >= 250000:
        return 15
    if karma >= 175000:
        return 14
    if karma >= 100000:
        return 13
    if karma >= 75000:
        return 12
    if karma >= 50000:
        return 11
    if karma >= 25000:
        return 10
    if karma >= 10000:
        return 9
    if karma >= 5000:
        return 8
    if karma >= 2500:
        return 7
    if karma >= 1000:
        return 6
    if karma >= 500:
        return 5
    if karma >= 250:
        return 4
    if karma >= 100:
        return 3
    if karma >= 10:
        return 2
    return 1

def users_list_query(sort_by="karma", run_query=True):
    sort_line = ""
    if sort_by == "postCount":
        sort_line = 'sort: {postCount: -1}'
    elif sort_by == "commentCount":
        sort_line = 'sort: {commentCount: -1}'
    else:
        sort_line = 'sort: {karma: -1}'
    query = ("""
        {
          users(input: {
            terms: {
              view: "LWUsersAdmin"
              limit: 500
              %s
            }
          }) {
            results {
              _id
              slug
              karma
              postCount
              commentCount
            }
          }
        }
    """ % sort_line)

    if not run_query:
        return query + ('''\n<a href="%s">Run this query</a>\n\n''' % (config.GRAPHQL_URL.replace("graphql", "graphiql") + "?query=" + quote(query)))
    request = util.send_query(query)
    return request.json()['data']['users']['results']


def show_users_list(sort_by, display_format):
    users = users_list_query(sort_by=sort_by, run_query=(False if display_format == "queries" else True))

    if display_format == "queries":
        result = "<pre>"
        result += users + "\n"
        result += "</pre>\n"
        return result

    result = """<!DOCTYPE html>
    <html>
    """
    result += util.show_head("Users list")
    result += "<body>\n"
    result += util.show_navbar(navlinks=[
            '''<a href="%s" title="Show all the GraphQL queries used to generate this page">Queries</a>''' % linkpath.userlist(display_format="queries")
        ])
    result += '''<div id="wrapper">'''
    result += '''<div id="content">'''

    result += ('''
        <table>
            <tr>
                <th>Username</th>
                <th>User ID</th>
                <th><a href="%s">Karma</a></th>
                <th>Small vote power</th>
                <th>Big vote power</th>
                <th><a href="%s">Post count</a></th>
                <th><a href="%s">Comment count</a></th>
            </tr>
    ''' % (
            linkpath.userlist(sort="karma"),
            linkpath.userlist(sort="postCount"),
            linkpath.userlist(sort="commentCount")
        )
    )

    for user in users:
        if user['slug'] is None:
            linked_user = "[deleted]"
        else:
            linked_user = '''<a href="%s">%s</a>''' % (linkpath.users(userslug=user['slug']), user['slug'])
        result += ('''
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td style="text-align: right;">%s</td>
                <td style="text-align: right;">%s</td>
                <td style="text-align: right;">%s</td>
                <td style="text-align: right;">%s</td>
                <td style="text-align: right;">%s</td>
            </tr>
        ''' % (
                linked_user,
                user['_id'],
                user['karma'],
                small_vote_power(user['karma']),
                big_vote_power(user['karma']),
                user['postCount'],
                user['commentCount']
            )
        )

    result += "</div>"  # content
    result += "</div>"  # wrapper
    result += "</body>"
    result += "</html>"

    return result


if __name__ == "__main__":
    arg_count = 2
    if len(sys.argv) != arg_count + 1:
        print("Unexpected number of arguments")
    else:
        print(show_users_list(sort_by=sys.argv[1], display_format=sys.argv[2]))
