#!/usr/bin/env python3

import sys
from urllib.parse import quote
import datetime

import config
import util
import linkpath


def get_content_for_post(postid, run_query=True):
    query = ("""
    {
      post(
        input: {
          selector: {
            _id: "%s"
          }
        }
      ) {
        result {
          _id
          postedAt
          url
          canonicalSource
          title
          slug
          commentCount
          htmlBody
          baseScore
          voteCount
          pageUrl
          legacyId
          question
          tableOfContents
          user {
            username
            displayName
            slug
            bio
          }
          coauthors {
            _id
            username
            displayName
            slug
          }
        }
      }
    }
    """ % postid)

    if not run_query:
        return query + ('''\n<a href="%s">Run this query</a>\n\n''' % (config.GRAPHQL_URL.replace("graphql", "graphiql") + "?query=" + quote(query)))

    request = util.send_query(query)
    try:
        return request.json()['data']['post']['result']
    except TypeError:
        return {'title': '', 'slug': '', 'baseScore': 0, 'voteCount': 0, 'pageUrl': '',
                'url': '', 'htmlBody': '', 'postedAt': '', 'commentCount': 0, 'legacyId': None,
                'user': {'slug': '', 'username': ''}, 'question': False,
                'tableOfContents': {'headingsCount': 0, 'html': "", 'sections': []}
               }


def get_comments_for_post(postid, view="postCommentsTop", run_query=True):
    query = ("""
    {
      comments(input: {
        terms: {
          view: "%s",
          postId: "%s",
        }
      }) {
        results {
          _id
          user {
            _id
            username
            displayName
            slug
            bio
          }
          userId
          author
          parentCommentId
          pageUrl
          htmlBody
          baseScore
          voteCount
          postedAt
        }
      }
    }
    """ % (view, postid))

    if not run_query:
        return query + ('''\n<a href="%s">Run this query</a>\n\n''' % (config.GRAPHQL_URL.replace("graphql", "graphiql") + "?query=" + quote(query)))

    request = util.send_query(query)
    result = []
    for comment in request.json()['data']['comments']['results']:
        result.append(comment)

    return result


def query_question_answers(postid, run_query=True):
    query = ("""
    {
      comments(input: {
        terms: {
          view: "questionAnswers",
          postId: "%s",
        }
      }) {
        results {
          _id
          user {
            _id
            username
            displayName
            slug
            bio
          }
          userId
          author
          parentCommentId
          pageUrl
          htmlBody
          baseScore
          voteCount
          postedAt
          answer
        }
      }
    }
    """ % postid)

    if not run_query:
        query_url = config.GRAPHQL_URL.replace("graphql", "graphiql") + "?query=" + quote(query)
        return query + ('''\n<a href="%s">Run this query</a>\n\n''' % query_url)

    request = util.send_query(query)
    result = []
    for answer in request.json()['data']['comments']['results']:
        result.append(answer)
    return result


def query_replies_to_answer(answer_id, run_query=True):
    query = ("""
    {
      comments(input: {
        terms: {
          view: "repliesToAnswer",
          parentAnswerId: "%s",
        }
      }) {
        results {
          _id
          user {
            _id
            username
            displayName
            slug
          }
          userId
          author
          parentCommentId
          pageUrl
          baseScore
          voteCount
          postedAt
          htmlBody
        }
      }
    }
    """ % answer_id)

    if not run_query:
        query_url = config.GRAPHQL_URL.replace("graphql", "graphiql") + "?query=" + quote(query)
        return query + ('''\n<a href="%s">Run this query</a>\n\n''' % query_url)

    request = util.send_query(query)
    result = []
    for comment in request.json()['data']['comments']['results']:
        result.append(comment)
    return result


class CommentTree(object):
    def __init__(self, commentid, data):
        self.commentid = commentid
        self.data = data
        self.children = []
        self.parity = None

    def __repr__(self):
        return self.commentid + "[" + str(self.children) + "]"

    def insert(self, child):
        self.children.append(child)


def build_comment_thread(comments):
    # Convert comments to tree nodes
    nodes = []
    for comment in comments:
        nodes.append(CommentTree(commentid=comment['_id'], data=comment))

    # Build index to be able to find nodes by their IDs
    index = {}
    for node in nodes:
        index[node.commentid] = node

    root = CommentTree("root", {})

    for node in nodes:
        parent = node.data['parentCommentId']
        if not parent:
            root.insert(node)
        else:
            try:
                index[parent].insert(node)
            except KeyError:
                # For some reason, comments sometimes refer to non-existent
                # parents, e.g. on post xuQ4dCHBtRXFZG487 there is a parent
                # called rjgZaK8uzHG3jAu2p that many comments refer to, but
                # this parent doesn't exist (and never existed, if you look at
                # the original post)
                # https://web.archive.org/web/20160824012747/http://effective-altruism.com/ea/10l/june_2016_givewell_board_meeting/
                root.insert(node)

    update_parity(root, "even")

    return root


def update_parity(comment_node, parity):
    comment_node.parity = parity
    for child in comment_node.children:
        child_parity = "even" if parity == "odd" else "odd"
        update_parity(child, child_parity)


def show_comment(comment_node):
    result = ""
    comment = comment_node.data
    color = config.COMMENT_COLOR if comment_node.parity == "odd" else "#FFFFFF"

    # If this is the root node, comment is {} so skip it
    if comment:
        commentid = comment['_id']
        result += ('''<div id="%s" style="border: 1px solid #B3B3B3; padding-left: 15px; padding-right: 0px; padding-bottom: 10px; padding-top: 10px; margin-left: 0px; margin-right: -1px; margin-bottom: 0px; margin-top: 10px; background-color: %s">''' % (commentid, color))
        result += "<details open>"
        result += "<summary>"
        if util.safe_get(comment, 'parentCommentId'):
            result += '''<a href="#%s" title="Go to parent comment">↑</a> ''' % util.safe_get(comment, 'parentCommentId')
        result += "comment by "
        result += util.userlink(slug=util.safe_get(comment, ['user', 'slug']),
                                username=util.safe_get(comment, ['user', 'username']),
                                display_name=util.safe_get(comment, ['user', 'displayName']),
                                bio=util.safe_get(comment, ['user', 'bio']))
        result += " ·\n"
        result += (('''<a href="#%s">''' % commentid) + comment['postedAt'] + "</a> · ")
        result += util.grouped_links(util.alt_urls(comment['pageUrl']))
        result += "</summary>"
        result += util.cleanHtmlBody(util.substitute_alt_links(comment['htmlBody']))
        if comment_node.children:
            result += '<span style="font-size: 14px;">Replies from: '
            replies = ['<a href="#%s">%s</a>' %
                       (child.commentid, util.safe_get(child.data, ['user', 'username']))
                       for child in comment_node.children]
            result += ", ".join(replies)
            result += '</span>'

    if comment_node.children:
        for child in comment_node.children:
            result += show_comment(child)

    if comment:
        result += "</details>"
        result += "</div>"

    return result


def show_answer(answer):
    result = ("""
    <div id="%s" style="border: 1px solid #B3B3B3; padding-left: 15px; padding-right: 0px; padding-bottom: 10px; padding-top: 10px; margin-left: 0px; margin-right: -1px; margin-bottom: 0px; margin-top: 10px;">
        answer by %s · <a href="#%s">%s</a> · %s
        <br>
        %s
    """ % (
        answer["_id"],
        util.userlink(slug=util.safe_get(answer, ["user", "slug"]),
                      username=answer["author"],
                      display_name=util.safe_get(answer, ["user", "displayName"]),
                      bio=util.safe_get(answer, ["user", "bio"])),
        answer["_id"],
        answer["postedAt"],
        util.grouped_links(util.alt_urls(util.safe_get(answer, "pageUrl"), is_answer=True)),
        util.cleanHtmlBody(util.substitute_alt_links(answer["htmlBody"])),
    ))
    replies = query_replies_to_answer(util.safe_get(answer, "_id"))
    root = build_comment_thread(replies)
    result += show_comment(root)
    result += "</div>"

    return result


def show_post_and_comment_thread(postid, display_format):
    print("""<!DOCTYPE html>
    <html>
    """)
    run_query = False if display_format == "queries" else True
    post = get_content_for_post(postid, run_query=run_query)
    if run_query:
        post_date = util.safe_get(post, 'postedAt', default="2018-01-01")
    else:
        post_date = "2018-01-01"
    # Apparently post_date is sometimes the empty string, so we have to check again
    if not post_date:
        post_date = "2018-01-01"
    if (run_query and "lesswrong" in config.GRAPHQL_URL and
        datetime.datetime.strptime(post_date[:len("2018-01-01")],
                                   "%Y-%m-%d") < datetime.datetime(2009, 2, 27)):
        comments = get_comments_for_post(postid, view="postCommentsOld", run_query=run_query)
        sorting_text = "oldest first, as this post is from before comment nesting was available (around 2009-02-27)."
    else:
        comments = get_comments_for_post(postid, run_query=run_query)
        sorting_text = "top scores."
    if (not run_query) or util.safe_get(post, "question"):
        answers = query_question_answers(postid, run_query=run_query)

    if display_format == "queries":
        result = "<pre>"
        result += post + "\n"
        result += comments + "\n"
        result += answers + "\n"
        result += "</pre>\n"
        return result

    if "user" in post and post["user"] and "slug" in post["user"] and post["user"]["slug"]:
        author = post['user']['slug']
    else:
        author = None
    canonical_url = util.safe_get(post, 'pageUrl')
    if util.safe_get(post, 'canonicalSource'):
        canonical_url = util.safe_get(post, 'canonicalSource')
    result = util.show_head(title=post['title'],
                            canonical_url=canonical_url,
                            author=author if author is not None else "[deleted]",
                            date=post['postedAt'],
                            publisher="LessWrong 2.0" if "lesswrong" in config.GRAPHQL_URL
                                       else "Effective Altruism Forum")
    result += "<body>\n"
    result += util.show_navbar(navlinks=[
            '''<a href="%s" title="Show all the GraphQL queries used to generate this page">Queries</a>''' % linkpath.posts(postid=util.htmlescape(postid), postslug=post['slug'], display_format="queries")
        ])
    result += '''<div id="wrapper">'''
    result += '''<div id="content">'''
    result += "<h1>" + util.htmlescape(post['title']) + "</h1>\n"
    result += "post by "
    result += util.userlink(slug=post.get("user", {}).get("slug", None),
                            username=post.get("user", {}).get("username", None),
                            display_name=post.get("user", {}).get("displayName", None),
                            bio=util.safe_get(post, ['user', 'bio']))
    for coauthor in util.safe_get(post, "coauthors", []):
        result += ", " + util.userlink(slug=util.safe_get(coauthor, "slug"),
                                       username=util.safe_get(coauthor, "username"),
                                       display_name=util.safe_get(coauthor, "displayName"))
    result += " ·\n"
    result += '''%s ·\n''' % post['postedAt']
    result += util.grouped_links(util.alt_urls(post['pageUrl'])) + " ·\n"
    if post['legacyId'] is not None:
        result += '''<a href="%s" title="Legacy link">Legacy</a> ·\n''' % util.legacy_link(post['legacyId'])

    if util.safe_get(post, "question") and util.safe_get(post, ["tableOfContents", "sections"]):
        result += '''<a href="#comments">''' + util.safe_get(post, ["tableOfContents", "sections"])[-1]["title"] + '</a>\n'
    else:
        result += '''<a href="#comments">''' + str(post['commentCount']) + ' comments</a>\n'

    if post['url'] is not None:
        result += ('''
            <p>This is a link post for <a href="%s">%s</a></p>
        '''% (post['url'], post['url']))
    if "question" in post and post["question"]:
        result += "<p>This is a question post.</p>"
    if "tableOfContents" in post and post["tableOfContents"] and "sections" in post["tableOfContents"]:
        if post["tableOfContents"]["sections"]:
            result += '''<h2>Contents</h2>\n'''
            result += '<pre style="font-size: 12px;">\n'
            for section in post["tableOfContents"]["sections"]:
                ans_title = util.safe_get(section, "title")
                if ans_title and section["level"] == 2:
                    ans_title = " ".join(ans_title.split()[1:])
                indent = " " * (2 * section["level"])
                result += '''%s<a href="#%s">%s</a>\n''' % (indent, section["anchor"],
                                                            ans_title)
            result += '</pre>\n'
            # post['htmlBody'] is HTML without the table of contents anchors added
            # in, so we have to use a separate HTML provided by the
            # tableOfContents JSON
            result += util.cleanHtmlBody(util.substitute_alt_links(util.safe_get(post, ['tableOfContents', 'html'])))
    else:
        result += util.cleanHtmlBody(util.substitute_alt_links(post['htmlBody']))

    if util.safe_get(post, "question"):
        result += '<h2 id="answers">Answers</h2>'
        for answer in answers:
            result += show_answer(answer)

    if util.safe_get(post, "question") and util.safe_get(post, ["tableOfContents", "sections"]):
        result += '''<h2 id="comments">''' + util.safe_get(post, ["tableOfContents", "sections"])[-1]["title"] + '</h2>\n'
    else:
        result += '''<h2 id="comments">''' + str(post['commentCount']) + ' comments</h2>'
    result += "<p>Comments sorted by %s</p>" % sorting_text

    root = build_comment_thread(comments)
    result += show_comment(root)

    result += ("""
    </div>
    </div>
        </body>
        </html>
    """)

    return result


if __name__ == "__main__":
    if len(sys.argv) != 2 + 1:
        print("Please enter a post ID and display format as argument")
    else:
        print(show_post_and_comment_thread(postid=sys.argv[1], display_format=sys.argv[2]))

