#!/usr/bin/env python3

import sys
from urllib.parse import quote
import datetime

import config
import util
import linkpath


def get_content_for_tag(tagslug, run_query=True):
    query = ("""
    {
      tag(
        input: {
          selector: {
            slug: "%s"
          }
        }
      ) {
        result {
          description {
            html
          }
        }
      }
    }
    """ % tagslug)

    if not run_query:
        return query + ('''\n<a href="%s">Run this query</a>\n\n''' % (config.GRAPHQL_URL.replace("graphql", "graphiql") + "?query=" + quote(query)))

    request = util.send_query(query, operation_name="get_content_for_tag")
    try:
        return request.json()['data']['tag']['result']
    except TypeError:
        return {}

def show_tag(tagslug, display_format):
    print("""<!DOCTYPE html>
    <html>
    """)
    run_query = False if display_format == "queries" else True
    tag_content = get_content_for_tag(tagslug, run_query=run_query)
    if display_format == "queries":
        result = "<pre>"
        result += tag_content + "\n"
        result += "</pre>\n"
        return result

    result = util.show_head(title=tagslug,
                             author="",
                             date="",
                             publisher="LessWrong 2.0" if "lesswrong" in config.GRAPHQL_URL
                                       else "Effective Altruism Forum",
                             widepage=True)
    result += "<body>\n"
    result += util.show_navbar(navlinks=[
            '''<a href="%s" title="Show all the GraphQL queries used to generate this page">Queries</a>''' % "TODO"
        ])
    result += '''<div id="wrapper">'''
    result += '''<div id="content">'''
    result += "<h1>" + util.htmlescape(tagslug) + "</h1>\n"
    result += " ·\n"
    result += util.cleanHtmlBody(util.substitute_alt_links(util.safe_get(tag_content, ['description', 'html'])))
    result += ("""
    </div>
    </div>
        </body>
        </html>
    """)

    return result


if __name__ == "__main__":
    if len(sys.argv) != 2 + 1:
        print("Please enter a tag slug and display format as argument")
    else:
        print(show_tag(tagslug=sys.argv[1], display_format=sys.argv[2]))

