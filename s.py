#!/usr/bin/env python3

import sys
from urllib.parse import quote
import datetime

import config
import util
import linkpath

def get_sequence(sid, run_query=True):
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
    """ % sid)

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
