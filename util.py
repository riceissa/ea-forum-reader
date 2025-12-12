#!/usr/bin/env python3

import requests
import datetime
import re
from urllib.parse import quote
import sys
from typing import Any

import linkpath
import config
import util

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

def get_from_request(request, keys, default=None) -> tuple[Any, int]:
    try:
        j = request.json()
        return (safe_get(j, keys, default=default), request.status_code)
    except:
        return (None, request.status_code)


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


def show_head(title, author="", date="", publisher="", widepage=False, canonical_url=""):
    result = ("""
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
        %s
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
    """ % (
            '''<meta name="author" content="%s">''' % htmlescape(author) if author else "",
            '''<meta name="dcterms.date" content="%s">''' % htmlescape(date) if date else "",
            '''<link rel="canonical" href="%s">''' % htmlescape(canonical_url) if canonical_url else "",
            htmlescape(title),
            htmlescape(title),
            '''<meta name="citation_author" content="%s">''' % htmlescape(author) if author else "",
            '''<meta name="citation_publication_date" content="%s">''' % htmlescape(date) if date else "",
            htmlescape(title),
            config.LINK_COLOR,
            config.LINK_COLOR
        )
    )

    result += ("""
            #wrapper {
              border-left: 1px solid #d2d2d2;
              border-right: 1px solid #d2d2d2;
              margin: 0 auto;
              overflow: hidden;
              background-color: #fff;
            }
            #content {
              padding: 30px 0 0 32px;
              background-color: #fff;
              float: left;
            }
            #sidebar {
              padding: 30px 32px 0 0;
              background-color: #fff;
              float: right;
            }

            @media (max-width: 768px) {
                #sidebar {
                    width: 100%;
                    float: none;
                    padding: 0 0 0 0;
                }
                #content {
                    width: 100%;
                    float: none;
                    padding: 0 0 0 0;
                }
                #wrapper {
                    width: 100%;
                    overflow: auto;
                }
            }
    """)

    if widepage:
        result += """
            #wrapper {
                max-width: 1500px;
            }
            #content {
            }
            #sidebar {
              width: 0px;
            }
        """
    else:
        result += """
        @media (min-width: 768px) {
            #wrapper {
              width: 1024px;
            }
            #content {
              width: 710px;
            }
            #sidebar {
              width: 220px;
            }
        }
        """

    result += """
        </style>
    </head>
    """

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


def send_query(query, operation_name=None):
    email = config.EMAIL
    headers = {'User-Agent': f'LW and EA Forum Reader (https://github.com/riceissa/ea-forum-reader; contact: {email})'}

    # The documentation
    # https://www.apollographql.com/docs/graphos/routing/security/csrf#configuring-csrf-prevention-in-the-router
    # does not say what the X-Apollo-Operation-Name value should be,
    # other than that it be non-empty. One of the LW devs suggested to me that
    # it would be good if the value somehow corresponded to the query, so for
    # now I've changed all calls to send_query to use the function name as the
    # operation_name.
    if operation_name:
        headers['X-Apollo-Operation-Name'] = operation_name
    else:
        headers['X-Apollo-Operation-Name'] = "default_operation"

    return requests.get(config.GRAPHQL_URL, params={'query': query}, headers=headers)

def error_message_string(content_type, content_id, status_code):
    result = "<pre>"
    result += f"Received a status code of {status_code} from the API endpoint.\n"
    if status_code == 403:
        service = "LessWrong" if "lesswrong" in config.GRAPHQL_URL else "the Effective Altruism Forum"
        result += f"This probably means that Issa's server is being blocked by {service}.\n"
    result += "You can view the content instead at:\n"
    if content_type == "posts":
        if "lesswrong" in config.GRAPHQL_URL:
            url = f"https://www.lesswrong.com/{content_type}/{content_id}"
        else:
            url = f"https://forum.effectivealtruism.org/{content_type}/{content_id}"
    elif content_type == "userlist":
        if "lesswrong" in config.GRAPHQL_URL:
            url = f"https://www.lesswrong.com/leaderboard"
        else:
            url = "https://forum.effectivealtruism.org/people-directory"
    else:
        if "lesswrong" in config.GRAPHQL_URL:
            url = "https://www.lesswrong.com/"
        else:
            url = "https://forum.effectivealtruism.org/"
    result += f'<a href="{url}">{url}</a>'
    result += "</pre>\n"
    return result

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


def userid_to_userslug(userid: str) -> tuple[str, int]:
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

    request = send_query(query, operation_name="userid_to_userslug")
    return util.get_from_request(request, ['data', 'user', 'result', 'slug'])


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
    return util.get_from_request(request, ['data', 'user', 'result', '_id'])


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
        "gw": "https://www.greaterwrong.com/posts/bnY3L48TtDrKTzGRb/ai-safety-success-stories#comment-9zAikCfT78BhyT8Aj",
        "gw_permalink": "https://www.greaterwrong.com/posts/bnY3L48TtDrKTzGRb/ai-safety-success-stories/comment/9zAikCfT78BhyT8Aj",
        "reader": "https://lw2.issarice.com/posts/bnY3L48TtDrKTzGRb/ai-safety-success-stories#9zAikCfT78BhyT8Aj"
    }
    For post URLs, the permalink keys will not exist."""
    anchor = None
    try:
        domain, path, comment_id = re.match(r'https?://((?:www|ea|forum)\.(?:greaterwrong\.com|effectivealtruism\.org|lesswrong\.com|alignmentforum\.org))(/posts/[a-zA-Z0-9]+/[^/]+)(?:/comment/|/answer/|#|#comment-|\?commentId=)([a-zA-Z0-9]+)$', original_url).groups()
        # Keep track of a list of common anchors that are not comment anchors
        if comment_id in ["comments"]:
            anchor = comment_id
            comment_id = None
    except AttributeError:
        try:
            domain, path = re.match(r'https?://((?:www|ea|forum)\.(?:greaterwrong\.com|effectivealtruism\.org|lesswrong\.com|alignmentforum\.org))(/posts/[a-zA-Z0-9]+/[^/]+|/users/[^/#]+)$', original_url).groups()
            comment_id = None
        except:
            print("We don't know how to deal with this URL: ", original_url, file=sys.stderr)
            return {"official": "?", "gw": "?", "reader": "?"}
    if domain in ["www.lesswrong.com", "forum.effectivealtruism.org", "www.alignmentforum.org"]:
        official_domain = domain
    elif domain == "www.greaterwrong.com":
        official_domain = "www.lesswrong.com"
    elif domain == "ea.greaterwrong.com":
        official_domain = "forum.effectivealtruism.org"

    if domain in ["forum.effectivealtruism.org", "ea.greaterwrong.com"]:
        gw_domain = "ea.greaterwrong.com"
        reader_domain = "eaforum.issarice.com"
    else:
        gw_domain = "www.greaterwrong.com"
        reader_domain = "lw2.issarice.com"

    if comment_id:
        # GW is the only weird one which distinguishes between comment vs
        # answer URL structure, but it only does this for the permalink, so the
        # anchor version still uses "#comment-" even for answers
        if is_answer:
            gw_permalink = "https://" + gw_domain + path + "/answer/" + comment_id
        else:
            gw_permalink = "https://" + gw_domain + path + "/comment/" + comment_id
        result = {
            "official": "https://" + official_domain + path + "#" + comment_id,
            "official_permalink": "https://" + official_domain + path + "?commentId=" + comment_id,
            "gw": "https://" + gw_domain + path + "#comment-" + comment_id,
            "gw_permalink": gw_permalink,
            "reader": "https://" + reader_domain + path + "#" + comment_id
        }
    else:
        result = {
            "official": "https://" + official_domain + path + ("#" + anchor if anchor else ""),
            "gw": "https://" + gw_domain + path + ("#" + anchor if anchor else ""),
            "reader": "https://" + reader_domain + path + ("#" + anchor if anchor else "")
        }
    return result

def grouped_links(url_dict):
    if "lesswrong.com" in url_dict["official"]:
        official_variant = "LW"
        official_title = "Official LessWrong 2.0"
    elif "forum.effectivealtruism.org" in url_dict["official"]:
        official_variant = "EA"
        official_title = "Official EA Forum"
    elif "alignmentforum.org" in url_dict["official"]:
        official_variant = "AF"
        official_title = "Official Alignment Forum"
    else:
        official_variant = "?"
        official_title = "?"

    if "official_permalink" in url_dict:
        result = '''<a title="%s link" href="%s">%s</a>(<a title="%s permalink" href="%s">p</a>) · <a title="GreaterWrong link" href="%s">GW</a>(<a title="GreaterWrong permalink" href="%s">p</a>)''' % (
                official_title, url_dict["official"], official_variant,
                official_title, url_dict["official_permalink"], url_dict["gw"],
                url_dict["gw_permalink"])
    else:
        result = '''<a title="%s link" href="%s">%s</a> · <a title="GreaterWrong link" href="%s">GW</a>''' % (
                official_title, url_dict["official"], official_variant, url_dict["gw"])

    return result


def convert_url(match):
    begin = match.group(1)
    original_url = match.group(2)
    end = match.group(3)
    url_dict = alt_urls(original_url)
    if url_dict["official"] != "?":
        html = begin + url_dict["reader"] + end + " [" + grouped_links(url_dict) + "]"
    else:
        html = begin + original_url + end + " [" + grouped_links(url_dict) + "]"
    return html

def substitute_alt_links(html_body):
    if not html_body:
        return ""
    result = html_body
    result = re.sub(r'(<a[^>]+href=")(https?://(?:www\.|forum\.)(?:lesswrong\.com|greaterwrong\.com|effectivealtruism\.org|alignmentforum\.org)/[^"]+)("[^>]*>.*?</a>)',
                    convert_url,
                    result)
    return result
