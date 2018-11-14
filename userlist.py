#!/usr/bin/env python3

import sys
from scrape import *


def users_list_query(run_query=True):
    query = """
        {
          users(input: {
            terms: {
              view: "LWUsersAdmin"
              limit: 500
              sort: {karma: -1}
            }
          }) {
            results {
              _id
              slug
              karma
            }
          }
        }
    """

    if not run_query:
        return query
    request = send_query(query)
    return request.json()['data']['users']['results']


def show_users_list(display_format):
    users = users_list_query(run_query=(False if display_format == "queries" else True))

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
            '''<a href="./userlist.php?format=queries" title="Show all the GraphQL queries used to generate this page">Queries</a>'''
        ])
    result += '''<div id="wrapper">'''
    result += '''<div id="content">'''

    result += '''
        <table>
            <tr>
                <th>Username</th>
                <th>Karma</th>
            </tr>
    '''

    for user in users:
        result += ('''
            <tr>
                <td><a href="./user.php?id=%s">%s</a></td>
                <td>%s</td>
            </tr>
        ''' % (
                user['slug'],
                user['slug'],
                user['karma']
            )
        )

    result += "</div>"  # content
    result += "</div>"  # wrapper
    result += "</body>"
    result += "</html>"

    return result


if __name__ == "__main__":
    arg_count = 1
    if len(sys.argv) != arg_count + 1:
        print("Unexpected number of arguments")
    else:
        print(show_users_list(display_format=sys.argv[1]))
