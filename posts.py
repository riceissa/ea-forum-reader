#!/usr/bin/env python3

import sys
from urllib.parse import quote

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
          title
          slug
          body
          commentsCount
          htmlBody
          baseScore
          voteCount
          pageUrl
          legacyId
          question
          %s
          user {
            username
            slug
          }
        }
      }
    }
    """ % (postid, "tableOfContents" if "lesswrong" in config.GRAPHQL_URL else ""))

    if not run_query:
        return query + ('''\n<a href="%s">Run this query</a>\n\n''' % (config.GRAPHQL_URL.replace("graphql", "graphiql") + "?query=" + quote(query)))

    request = util.send_query(query)
    try:
        return request.json()['data']['post']['result']
    except TypeError:
        return {'title': '', 'slug': '', 'baseScore': 0, 'voteCount': 0, 'pageUrl': '',
                'url': '', 'htmlBody': '', 'postedAt': '', 'commentsCount': 0, 'legacyId': None,
                'user': {'slug': '', 'username': ''}, 'question': False,
                'tableOfContents': {'headingsCount': 0, 'html': "", 'sections': []}
               }


def get_comments_for_post(postid, run_query=True):
    query = ("""
    {
      comments(input: {
        terms: {
          view: "postCommentsTop",
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
          }
          userId
          author
          parentCommentId
          pageUrl
          body
          htmlBody
          baseScore
          voteCount
          postedAt
        }
      }
    }
    """ % postid)

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
        if comment['user'] and comment['user']['slug'] and comment['user']['username']:
            result += '''comment by <b><a href="%s">%s</a></b> ·\n''' % (linkpath.users(userslug=comment['user']['slug']), comment['user']['username'])
        else:
            result += '''comment by <b>[deleted]</b> ·\n'''
        result += (('''<a href="#%s">''' % commentid) + comment['postedAt'] + "</a> · ")
        result += ("score: " + str(comment['baseScore']) + " (" + str(comment['voteCount']) + " votes) · ")
        if "lesswrong" in config.GRAPHQL_URL:
            result += ('<a title="Official LessWrong 2.0 link" href="' + comment['pageUrl'] + '">LW</a> · ')
        else:
            result += ('<a title="Official EA Forum link" href="' + comment['pageUrl'] + '">EA</a> · ')
        result += '<a title="GreaterWrong link" href="' + util.ea_forum_to_gw(comment['pageUrl']) + '">GW</a>'
        result += util.cleanHtmlBody(util.substitute_alt_links(comment['htmlBody']))

    if comment_node.children:
        for child in comment_node.children:
            result += show_comment(child)

    result += ("</div>")

    return result


def show_answer(answer):
    result = ""
    result += ("""
    <div id="%s" style="border: 1px solid #B3B3B3; padding-left: 15px; padding-right: 0px; padding-bottom: 10px; padding-top: 10px; margin-left: 0px; margin-right: -1px; margin-bottom: 0px; margin-top: 10px;">
        answer by %s · %s · score: %s (%s votes)
        <br><br>
        %s
    </div>
    """ % (
        answer["_id"],
        answer["author"],
        answer["postedAt"],
        answer["baseScore"],
        answer["voteCount"],
        answer["htmlBody"],
    ))

    return result


def show_post_and_comment_thread(postid, display_format):
    print("""<!DOCTYPE html>
    <html>
    """)
    run_query = False if display_format == "queries" else True
    post = get_content_for_post(postid, run_query=run_query)
    comments = get_comments_for_post(postid, run_query=run_query)
    if (not run_query) or ("question" in post and post["question"]):
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
    result = util.show_head(title=post['title'],
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
    if author:
        result += '''post by <b><a href="%s">%s</a></b> ·\n''' % (linkpath.users(userslug=author), author)
    else:
        result += '''post by <b>[deleted]</b> ·\n'''
    result += '''%s ·\n''' % post['postedAt']
    result += '''score: %s (%s votes) ·\n''' % (post['baseScore'], post['voteCount'])
    if "lesswrong" in config.GRAPHQL_URL:
        result += '''<a href="%s" title="Official LessWrong 2.0 link">LW</a> ·\n''' % post['pageUrl']
    else:
        result += '''<a href="%s" title="Official EA Forum link">EA</a> ·\n''' % post['pageUrl']
    result += '''<a href="%s" title="GreaterWrong link">GW</a> ·\n''' % util.ea_forum_to_gw(post['pageUrl'])
    if post['legacyId'] is not None:
        result += '''<a href="%s" title="Legacy link">Legacy</a> ·\n''' % util.legacy_link(post['legacyId'])

    result += '''<a href="#comments">''' + str(post['commentsCount']) + ' comments</a>\n'

    if post['url'] is not None:
        result += ('''
            <p>This is a link post for <a href="%s">%s</a></p>
        '''% (post['url'], post['url']))
    if "question" in post and post["question"]:
        result += "<p>This is a question post.</p>"
    if "tableOfContents" in post and post["tableOfContents"] and "sections" in post["tableOfContents"]:
        if post["tableOfContents"]["sections"]:
            result += '''<h2>Contents</h2>
                <ul>'''
            for section in post["tableOfContents"]["sections"]:
                result += '''<li><a href="#%s">%s</a></li>''' % (section["anchor"], section["title"])
            result += '''</ul>'''
            # post['htmlBody'] is HTML without the table of contents anchors added
            # in, so we have to use a separate HTML provided by the
            # tableOfContents JSON
            result += util.cleanHtmlBody(util.substitute_alt_links(post['tableOfContents']['html']))
    else:
        result += util.cleanHtmlBody(util.substitute_alt_links(post['htmlBody']))

    if "question" in post and post["question"]:
        for answer in answers:
            result += show_answer(answer)

    result += '''<h2 id="comments">''' + str(post['commentsCount']) + ' comments</h2>'

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
        print("Please enter a post ID as argument")
    else:
        print(show_post_and_comment_thread(postid=sys.argv[1], display_format=sys.argv[2]))

