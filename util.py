#!/usr/bin/env python3

import requests
import datetime
import re
from urllib.parse import quote

import linkpath
import config

def htmlescape(string):
    return string.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&#34;')


def ea_forum_to_gw(ea_forum_link):
    if "forum.effectivealtruism.org" in config.GRAPHQL_URL:
        return ea_forum_link.replace('forum.effectivealtruism.org', 'ea.greaterwrong.com', 1)
    else:
        return ea_forum_link.replace('www.lesswrong.com', 'www.greaterwrong.com', 1)


def int_to_base36(number):
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
    base36 = ''
    while base36 == '' or number > 0:
        number, i = divmod(int(number), 36)
        base36 = alphabet[i] + base36
    return base36


def legacy_link(legacy_slug):
    slug = int_to_base36(legacy_slug)
    if "forum.effectivealtruism.org" in config.GRAPHQL_URL:
        return 'https://web.archive.org/web/*/http://effective-altruism.com/ea/%s/*' % slug
    else:
        return 'https://web.archive.org/web/*/http://lesswrong.com/lw/%s/*' % slug


def show_head(title, author="", date="", publisher=""):
    result = ("""
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
        %s
        %s
        <meta property="og:title" content="%s" />
        <meta property="og:locale" content="en_US" />
        <meta property="og:type" content="article" />
        <meta name="citation_title" content="%s">
        %s
        %s
        <meta name="citation_fulltext_world_readable" content="">
        <title>%s</title>
        <style type="text/css">
            body {
                font-family: Lato, Helvetica, sans-serif;
                font-size: 16px;
                line-height: 1.4;
                background-color: whitesmoke;
            }
            a {
                color: %s;
                text-decoration: underline;
            }
            a:visited {
                color: #8a8a8b;
            }
            blockquote {
                border-left: 2px solid #369;
                padding-left: 10px;
                margin-right: 15px;
                margin-left: 0px;
            }
            h1 {
                color: %s;
            }
            img {
                max-width: 100%%;
                height: auto;
            }
            table {
                background-color: #f9f9f9;
                border-collapse: collapse;
                border-bottom: none;
                border-top: none;
            }
            table th {
                background-color: #f2f2f2;
                border: 1px solid #aaaaaa;
                font-weight: bold;
                padding: 5px 10px;
            }
            table td {
                border: 1px solid #aaaaaa;
                padding: 5px 10px;
            }

            /* See https://stackoverflow.com/a/34259648/3422337 */
            .spoiler { border: 1px solid black; }
            .spoiler, .spoiler > * { transition: color 0.5s, opacity 0.5s; }
            .spoiler:not(:hover) { color: transparent; }
            .spoiler:not(:hover) > * { opacity: 0; }

            #wrapper {
              border-left: 1px solid #d2d2d2;
              border-right: 1px solid #d2d2d2;
              margin: 0 auto;
              width: 1024px;
              overflow: hidden;
              background-color: #fff;
            }
            #content {
              padding: 30px 0 0 32px;
              background-color: #fff;
              width: 710px;
              float: left;
            }
            #sidebar {
              padding: 30px 32px 0 0;
              background-color: #fff;
              width: 220px;
              float: right;
            }
        </style>
    </head>
    """ % (
            '''<meta name="author" content="%s">''' % htmlescape(author) if author else "",
            '''<meta name="dcterms.date" content="%s">''' % htmlescape(date) if date else "",
            htmlescape(title),
            htmlescape(title),
            '''<meta name="citation_author" content="%s">''' % htmlescape(author) if author else "",
            '''<meta name="citation_publication_date" content="%s">''' % htmlescape(date) if date else "",
            htmlescape(title),
            config.LINK_COLOR,
            config.LINK_COLOR
        )
    )

    return result


def show_navbar(navlinks=None, search_value=""):
    if navlinks is None:
        navlinks = []

    result = ("""<nav><a href="/">Home</a> ·
        <a href="https://github.com/riceissa/ea-forum-reader">About</a> ·
        <a href="%s">User list</a>
        """ % linkpath.userlist())

    for link in navlinks:
        result += " · " + link

    if search_value:
        search_value = 'value="%s"' % htmlescape(search_value)

    result += ("""
        <form action="%s" method="get" style="display: inline-block;">
                <input name="q" type="text" %s/>
                <input type="submit" value="Search" />
        </form>
    </nav>
    """ % (linkpath.search(), search_value))

    return result


def send_query(query):
    return requests.get(config.GRAPHQL_URL, params={'query': query})


def cleanHtmlBody(htmlBody):
    """For some reason htmlBody values often have the following tags that
    really shouldn't be there."""
    if htmlBody is None:
        return ""
    return (htmlBody.replace("<html>", "")
                    .replace("</html>", "")
                    .replace("<body>", "")
                    .replace("</body>", "")
                    .replace("<head>", "")
                    .replace("</head>", ""))


def userid_to_userslug(userid):
    query = ("""
    {
      user(input: {selector: {documentId: "%s"}}) {
        result {
          _id
          slug
        }
      }
    }
    """ % userid)

    request = send_query(query)
    return request.json()['data']['user']['result']['slug']


def userslug_to_userid(userslug, run_query=True):
    query = ("""
    {
      user(input: {selector: {slug: "%s"}}) {
        result {
          _id
          slug
        }
      }
    }
    """ % userslug)

    if not run_query:
        return query + ('''\n<a href="%s">Run this query</a>\n\n''' % (config.GRAPHQL_URL.replace("graphql", "graphiql") + "?query=" + quote(query)))

    request = send_query(query)
    return request.json()['data']['user']['result']['_id']


def substitute_alt_links(html_body):
    if not html_body:
        return ""
    if "lesswrong" in config.GRAPHQL_URL:
        return re.sub(r'(<a[^>]+href=)"https?://www\.lesswrong\.com/([^"]+)"([^>]*>)([^<]*</a>)',
                      r'\1"https://lw2.issarice.com/\2"\3\4 [<a href="https://www.lesswrong.com/\2">LW</a> · <a href="https://www.greaterwrong.com/\2">GW</a>]',
                      html_body)
    else:
        return re.sub(r'(<a[^>]+href=)"https?://forum\.effectivealtruism\.org/([^"]+)"([^>]*>)([^<]*</a>)',
                      r'\1"https://eaforum.issarice.com/\2"\3\4 [<a href="https://forum.effectivealtruism.org/\2">EA</a> · <a href="https://ea.greaterwrong.com/\2">GW</a>]',
                      html_body)
        # return re.sub(r'(<a\W+href=)"(https?://forum\.effectivealtruism\.org/[^"]+)"',
        #               r'\1"https://eaforum.issarice.com/\2"',
        #               html_body)
