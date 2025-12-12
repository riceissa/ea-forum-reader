#!/usr/bin/env python3

import sys
from urllib.parse import quote
from typing import Any

import config
import util
import linkpath


def comments_to_posts_ratio(comment_count, post_count):
    if not comment_count:
        comment_count = 0
    if not post_count:
        post_count = 0
    if post_count == 0 and comment_count == 0:
        return "n.a."
    elif post_count == 0:
        return "∞"
    else:
        return round(int(comment_count) / int(post_count), 1)

def small_vote_power(karma):
    """See
    https://github.com/LessWrong2/Lesswrong2/blob/devel/packages/lesswrong/lib/voting/new_vote_types.ts
    for the vote power implementation. See also the blog post at
    https://lw2.issarice.com/posts/7Sx3CJXA7JHxY2yDG/strong-votes-update-deployed#Vote_Power_by_Karma"""
    if karma is None:
        return 1
    if karma >= 1000:
        return 2
    return 1


def big_vote_power(karma):
    """See
    https://github.com/LessWrong2/Lesswrong2/blob/devel/packages/lesswrong/lib/voting/new_vote_types.ts
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

def users_list_query(sort_by: str = "karma", run_query : bool = True) -> tuple[Any, int] | str:
    sort_line = ""
    if sort_by == "postCount":
        sort_line = 'sort: {postCount: -1}'
    elif sort_by == "commentCount":
        sort_line = 'sort: {commentCount: -1}'
    elif sort_by == "afKarma":
        sort_line = 'sort: {afKarma: -1}'
    elif sort_by == "afPostCount":
        sort_line = 'sort: {afPostCount: -1}'
    elif sort_by == "afCommentCount":
        sort_line = 'sort: {afCommentCount: -1}'
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
              afKarma
              afPostCount
              afCommentCount
            }
          }
        }
    """ % sort_line)

    if not run_query:
        return query + ('''\n<a href="%s">Run this query</a>\n\n''' % (config.GRAPHQL_URL.replace("graphql", "graphiql") + "?query=" + quote(query)))
    request = util.send_query(query, operation_name="users_list_query")
    return util.get_from_request(request, ['data', 'users', 'results'])


def show_users_list(sort_by, display_format):
    users_and_status_code = users_list_query(sort_by=sort_by, run_query=(False if display_format == "queries" else True))
    if isinstance(users_and_status_code, str):
        users = users_and_status_code
    else:
        users, status_code = users_and_status_code
        if status_code != 200:
            util.error_message_string("userlist", "", status_code)

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
        <table style="font-size: 13px;">
            <tr>
                <th>Username</th>
                <th>User ID</th>
                <th><a href="%s">Karma</a></th>
                <th>Small vote power</th>
                <th>Big vote power</th>
                <th><a href="%s">Post count</a></th>
                <th><a href="%s">Comment count</a></th>
                <th>Comments:posts ratio</th>
                <th><a href="%s">AF karma</a></th>
                <th><a href="%s">AF post count</a></th>
                <th><a href="%s">AF comment count</a></th>
            </tr>
    ''' % (
            linkpath.userlist(sort="karma"),
            linkpath.userlist(sort="postCount"),
            linkpath.userlist(sort="commentCount"),
            linkpath.userlist(sort="afKarma"),
            linkpath.userlist(sort="afPostCount"),
            linkpath.userlist(sort="afCommentCount")
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
                user['commentCount'],
                comments_to_posts_ratio(user['commentCount'], user['postCount']),
                util.safe_get(user, 'afKarma'),
                util.safe_get(user, 'afPostCount'),
                util.safe_get(user, 'afCommentCount')
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
