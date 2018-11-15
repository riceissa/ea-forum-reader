#!/usr/bin/env python3

import sys
from scrape import *

import linkpath

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
        return query
    request = send_query(query)
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
    result += show_head("Users list")
    result += "<body>\n"
    result += show_navbar(navlinks=[
            '''<a href="%s" title="Show all the GraphQL queries used to generate this page">Queries</a>''' % linkpath.userlist(display_format="queries")
        ])
    result += '''<div id="wrapper">'''
    result += '''<div id="content">'''

    result += ('''
        <table>
            <tr>
                <th>Username</th>
                <th><a href="%s">Karma</a></th>
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
        result += ('''
            <tr>
                <td><a href="%s">%s</a></td>
                <td style="text-align: right;">%s</td>
                <td style="text-align: right;">%s</td>
                <td style="text-align: right;">%s</td>
            </tr>
        ''' % (
                linkpath.users(userslug=user['slug']),
                user['slug'],
                user['karma'],
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
