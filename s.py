#!/usr/bin/env python3
import pdb

import sys
from urllib.parse import quote
import datetime

import config
import util
import linkpath

def get_sequence(sequenceid, run_query=True):
    query = ("""
    {
      sequence(
        input: {
          selector: {
            _id: "%s"
          }
        }
      ) {
        result {
          title
          user {
            _id
            username
          }
          userId
          createdAt
          canonicalCollection {
            createdAt
            userId
            title
            slug
            gridImageId
            firstPageLink
            version
            _id
            schemaVersion
          }
          contents {
            html
            _id
          }
          chapters {
            createdAt
            title
            subtitle
            number
            sequenceId
            _id
          }
        }
      }
    }
    """ % sequenceid)

    if not run_query:
        return query + ('''\n<a href="%s">Run this query</a>\n\n''' % (config.GRAPHQL_URL.replace("graphql", "graphiql") + "?query=" + quote(query)))

    request = util.send_query(query)
    return util.safe_get(request.json(), ['data', 'sequence', 'result'])


def get_chapter(chapterid, run_query=True):
    query = ("""
    {
      chapter(
        input: {
          selector: {
            _id: "%s"
          }
        }
      ) {
        result {
          posts {
            title
            pageUrl
          }
        }
      }
    }
    """ % chapterid)

    if not run_query:
        return query + ('''\n<a href="%s">Run this query</a>\n\n''' % (config.GRAPHQL_URL.replace("graphql", "graphiql") + "?query=" + quote(query)))

    request = util.send_query(query)
    return util.safe_get(request.json(), ['data', 'chapter', 'result'])


def show_sequence(sequenceid, display_format):
    result = ("""<!DOCTYPE html>
    <html>
    """)
    run_query = False if display_format == "queries" else True
    sequence = get_sequence(sequenceid)
    result = util.show_head(title=util.safe_get(sequence, "title"),
                             author=util.safe_get(sequence, ["user", "username"]),
                             date=util.safe_get(sequence, "createdAt"),
                             publisher="LessWrong 2.0" if "lesswrong" in config.GRAPHQL_URL
                                       else "Effective Altruism Forum")
    result += "<body>\n"
    # result += util.show_navbar(navlinks=[
    #         '''<a href="%s" title="Show all the GraphQL queries used to generate this page">Queries</a>''' % linkpath.posts(postid=util.htmlescape(postid), postslug=post['slug'], display_format="queries")
    #     ])
    result += '''<div id="wrapper">'''
    result += '''<div id="content">'''
    result += "<h1>" + util.safe_get(sequence, "title") + "</h1>\n"
    for chapterdict in util.safe_get(sequence, "chapters"):
        chapterid = chapterdict["_id"]
        chapter = get_chapter(chapterid)
        result += "<h2>" + util.safe_get(chapterdict, "title") + "</h2>"
        result += "<ul>\n"
        for postdict in util.safe_get(chapter, "posts"):
            alt_urls = util.alt_urls(util.safe_get(postdict, "pageUrl"))
            result += '''  <li><a href="%s">%s</a></li>\n''' % (
                    alt_urls['reader'],
                    util.safe_get(postdict, "title")
                    )
        result += "</ul>\n"
    result += ("""
    </div>
    </div>
        </body>
        </html>
    """)
    return result

if __name__ == "__main__":
    if len(sys.argv) != 2 + 1:
        print("Please enter a sequence ID and display format as argument")
    else:
        print(show_sequence(sequenceid=sys.argv[1], display_format=sys.argv[2]))

