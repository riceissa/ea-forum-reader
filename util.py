#!/usr/bin/env python3

import requests
import datetime
import re
from urllib.parse import quote

import linkpath
import config

def htmlescape(string):
    return string.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&#34;')


def _safe_get(obj, key, default=None):
    """This acts like obj.get(key, default), except that if obj[key] exists but
    is None, we still return default rather than the accessed result. Also, if
    obj happens to be None, we return default rather than raising an exception.

    To see the difference, suppose obj = {"a": None}. Then obj.get("a", 1) is
    None but _safe_get(obj, "a", 1) is 1.

    Since obj can be None, _safe_get can also be nested without checking for
    None each time: _safe_get(_safe_get({}, "a"), "b", 1) is 1. Thus in some
    cases a default need only be specified at the end."""
    if obj is None:
        return default
    result = obj.get(key)
    if result is None:
        result = default
    return result


def _safe_multiget(obj, key_list, default=None):
    """This acts like _safe_get(_safe_get(obj, key1), key2, default). The
    intention is something like, get each key in turn, and return default is we
    get a None at any point."""
    if len(key_list) < 1:
        return obj
    result = obj
    for key in key_list[:-1]:
        result = _safe_get(result, key)
    return _safe_get(result, key_list[-1], default)


def safe_get(obj, keys, default=None):
    if isinstance(keys, list):
        return _safe_multiget(obj, keys, default)
    else:
        return _safe_get(obj, keys, default)


def official_url_to_gw(ea_forum_link):
    if "forum.effectivealtruism.org" in config.GRAPHQL_URL:
        return ea_forum_link.replace('forum.effectivealtruism.org', 'ea.greaterwrong.com', 1)
    else:
        return ea_forum_link.replace('www.lesswrong.com', 'www.greaterwrong.com', 1)

def official_url_to_reader(ea_forum_link):
    if "forum.effectivealtruism.org" in config.GRAPHQL_URL:
        return ea_forum_link.replace('forum.effectivealtruism.org', 'eaforum.issarice.com', 1)
    else:
        return ea_forum_link.replace('www.lesswrong.com', 'lw2.issarice.com', 1)

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
                font-size: 15.4px;
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
            code {
                background-color: #f6f6f6;
                padding-left: 4px;
                padding-right: 4px;
                word-wrap: normal;
            }
            pre code {
                display: block;
                line-height: 1.2;
                overflow: auto;
                padding: 10px;
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
            .spoilers { border: 1px solid black; }
            .spoilers, .spoilers > * { transition: color 0.5s, opacity 0.5s; }
            .spoilers:not(:hover) { color: transparent; }
            .spoilers:not(:hover) > * { opacity: 0; }
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

            @media (max-width: 768px) {
                #sidebar {
                    width: 100%%;
                    float: none;
                    padding: 0 0 0 0;
                }
                #content {
                    width: 97%%;
                    float: none;
                    padding: 0 0 0 0;
                }
                #wrapper {
                    width: 100%%;
                    overflow: auto;
                }
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


def userlink(slug=None, username=None, display_name=None, bio=None):
    if slug:
        displayed = username if username else slug
        if display_name and display_name != displayed:
            displayed = display_name + " (" + displayed + ")"
        url = linkpath.users(userslug=slug)
        if bio:
            return '''<a href="%s" title="%s">%s</a>''' % (url, htmlescape(bio), displayed)
        else:
            return '''<a href="%s">%s</a>''' % (url, displayed)
    else:
        return '''<b>[deleted]</b>'''

def official_link(page_url):
    if "lesswrong" in config.GRAPHQL_URL:
        return '''<a href="%s" title="Official LessWrong 2.0 link">LW</a>''' % page_url
    else:
        return '''<a href="%s" title="Official EA Forum link">EA</a>''' % page_url


def gw_link(page_url):
    return '''<a href="%s" title="GreaterWrong link">GW</a>''' % official_url_to_gw(page_url)

def alt_urls(original_url, is_answer=False):
    """Return a dictionary of URLs for all the alternative services (official,
    GW, my reader). Supported keys are: official, official_permalink, gw,
    gw_permalink, reader.

    For example, if the URL is "https://www.lesswrong.com/posts/bnY3L48TtDrKTzGRb/ai-safety-success-stories#9zAikCfT78BhyT8Aj" then the result is
    {
        "official": "https://www.lesswrong.com/posts/bnY3L48TtDrKTzGRb/ai-safety-success-stories#9zAikCfT78BhyT8Aj",
        "official_permalink": "https://www.lesswrong.com/posts/bnY3L48TtDrKTzGRb/ai-safety-success-stories?commentId=9zAikCfT78BhyT8Aj",
        "gw": "https://www.greaterwrong.com/posts/bnY3L48TtDrKTzGRb/ai-safety-success-stories#comment-9zAikCfT78BhyT8Aj"
        "gw_permalink": "https://www.greaterwrong.com/posts/bnY3L48TtDrKTzGRb/ai-safety-success-stories/comment/9zAikCfT78BhyT8Aj",
        "reader": "https://lw2.issarice.com/posts/bnY3L48TtDrKTzGRb/ai-safety-success-stories#9zAikCfT78BhyT8Aj"
    }
    For post URLs, the permalink keys will not exist.

    """
    result = {}
    for official in ["lesswrong.com", "forum.effectivealtruism.org", "alignmentforum.org"]:
        gw_subdomain = {"lesswrong.com": "www",
                        "forum.effectivealtruism.org": "ea",
                        "alignmentforum.org": "www"}[official]
        reader_subdomain  = {"lesswrong.com": "lw2",
                             "forum.effectivealtruism.org": "eaforum",
                             "alignmentforum.org": "lw2"}[official]
        if official in original_url:
            result['official'] = original_url
            if "#" in original_url:
                # For example, "http://example.com/page#blah" becomes
                # ("http://example.com/page", "blah")
                anchor_idx = original_url.rfind('#')
                base_url = original_url[:anchor_idx]
                anchor_text = original_url[anchor_idx+1:]
                result['official_permalink'] = base_url + '?commentId=' + anchor_text
                if official in original_url:
                    result['gw'] = base_url.replace(official, gw_subdomain + '.greaterwrong.com', 1) + "#comment-" + anchor_text
                    if is_answer:
                        result['gw_permalink'] = base_url.replace(official, gw_subdomain + '.greaterwrong.com', 1) + "/answer/" + anchor_text
                    else:
                        result['gw_permalink'] = base_url.replace(official, gw_subdomain + '.greaterwrong.com', 1) + "/comment/" + anchor_text
            else:
                base_url = original_url
                anchor_text = ""
                result['gw'] = original_url.replace(official, gw_subdomain + '.greaterwrong.com', 1)
                result['reader'] = original_url.replace(official, gw_subdomain + '.issarice.com', 1)
    if "greaterwrong.com" in original_url:
        pass


def _alt_links(original_url):
    if "lesswrong.com" in original_url or "www.greaterwrong.com" in original_url:
        official_variant = "LW"
        official_title = "Official LessWrong 2.0"
    elif "forum.effectivealtruism.org" in original_url or "ea.greaterwrong.com" in original_url:
        official_variant = "EA"
        official_title = "Official EA Forum"
    elif "alignmentforum.org" in original_url:
        official_variant = "AF"
        official_title = "Official Alignment Forum"
    else:
        official_variant = "?"
        official_title = "?"

    if ???:
        result = '''<a title="%s link" href="%s">%s</a> · <a title="GreaterWrong link" href="%s">GW</a>''' % (official_title, official_url, official_variant, gw_url)
    else:
        result = '''<a title="%s link" href="%s">%s</a>(<a title="%s permalink" href="%s">p</a>) · <a title="GreaterWrong link" href="%s">GW</a>(<a title="GreaterWrong permalink" href="%s">p</a>)''' % ()

def convert_url(match):
    begin = match.group(1)
    url = match.group(2)
    end = match.group(3)
    # TODO the problem is if this url is a greaterwrong one, especially a /comment/ one. then we can't just run a simple .replace() over it.
    # also the problem is that for links in the navbar (e.g. for posts and comments) there is no reader link, but for links that appear in thebody of a post/comment, then we do want to have a reader link.
    reader_url = official_url_to_reader(url)
    gw_url = official_url_to_gw(url)
    html = begin + reader_url + end + " [" + alt_links(url) + "]"
    return html

def substitute_alt_links(html_body):
    if not html_body:
        return ""
    result = html_body
    result = re.sub(r'(<a[^>]+href=")(https?://(?:www\.|forum\.)(?:lesswrong\.com|greaterwrong\.com|effectivealtruism\.org|alignmentforum\.org)/[^"]+)("[^>]*>.*?</a>)',
                    convert_url,
                    result)
    # result = re.sub(r'(<a[^>]+href=)"https?://(?:www\.)lesswrong\.com/([^"]+)"([^>]*>)(.*?</a>)',
    #                 r'\1"https://lw2.issarice.com/\2"\3\4 [<a href="https://www.lesswrong.com/\2">LW</a> · <a href="https://www.greaterwrong.com/\2">GW</a>]',
    #                 result)
    # result = re.sub(r'(<a[^>]+href=)"https?://(?:www\.)lesserwrong\.com/([^"]+)"([^>]*>)(.*?</a>)',
    #                 r'\1"https://lw2.issarice.com/\2"\3\4 [<a href="https://www.lesserwrong.com/\2">LW</a> · <a href="https://www.greaterwrong.com/\2">GW</a>]',
    #                 result)
    # result = re.sub(r'(<a[^>]+href=)"https?://forum\.effectivealtruism\.org/([^"]+)"([^>]*>)(.*?</a>)',
    #                 r'\1"https://eaforum.issarice.com/\2"\3\4 [<a href="https://forum.effectivealtruism.org/\2">EA</a> · <a href="https://ea.greaterwrong.com/\2">GW</a>]',
    #                 result)
    # result = re.sub(r'(<a[^>]+href=)"https?://(?:www\.)alignmentforum\.org/([^"]+)"([^>]*>)(.*?</a>)',
    #                 r'\1"https://lw2.issarice.com/\2"\3\4 [<a href="https://www.alignmentforum.org/\2">AF</a> · <a href="https://www.greaterwrong.com/\2">GW</a>]',
    #                 result)
    return result
