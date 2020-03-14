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
    print("""<!DOCTYPE html>
    <html>
    """)
    run_query = False if display_format == "queries" else True
    sequence = get_sequence(sequenceid)
    for chapterdict in util.safe_get(sequence, "chapters"):
        chapterid = chapterdict["_id"]
        chapter = get_chapter(chapterid)
        print("Chapter:", util.safe_get(chapterdict, "title"))
        for postdict in util.safe_get(chapter, "posts"):
            print("  post:", util.safe_get(postdict, "title"))
