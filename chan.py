#!/usr/bin/env python3

import sys
from urllib.parse import quote
import datetime

import config
import util
import linkpath
import posts

def show_post_and_comment_thread(postid: str, display_format: str) -> str:
    print("""<!DOCTYPE html>
    <html>
    """)
    run_query = False if display_format == "queries" else True
    post_and_status_code = posts.get_content_for_post(postid, run_query=run_query)
    if isinstance(post_and_status_code, str):
        return "Returning since only want to display the queries."
    post, status_code = post_and_status_code
    if status_code != 200:
        return util.error_message_string("posts", postid, status_code)
    comments = posts.get_comments_for_post(postid, view="postCommentsOld", run_query=run_query)
    if (not run_query) or util.safe_get(post, "question"):
        answers = posts.query_question_answers(postid, run_query=run_query)

    print("""
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
        <style type="text/css">
            body {
                font-family: arial,helvetica,sans-serif;
                font-size: 10pt;
            }
            blockquote {
                color: #789922;
                padding: 0;
                margin: 0;
            }
            blockquote:before {
                content: ">";
            }
            a.reply-parent {
                color: #d00;
            }
        </style>
    </head>
    """)

    result = "<body>\n"
    result += util.show_navbar()
    result += '''<div id="wrapper">'''
    result += '''<div id="content">'''
    result += "<h1>" + util.htmlescape(post['title']) + "</h1>\n"
    result += " ·\n"
    result += '''%s ·\n''' % post['postedAt']
    result += util.official_link(post['pageUrl']) + ' ·\n'
    result += util.gw_link(post['pageUrl']) + ' ·\n'

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
                indent = " " * (2 * section["level"])
                result += '''%s<a href="#%s">%s</a>\n''' % (indent, section["anchor"],
                                                            util.safe_get(section, "title"))
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
            result += posts.show_answer(answer)

    if util.safe_get(post, "question") and util.safe_get(post, ["tableOfContents", "sections"]):
        result += '''<h2 id="comments">''' + util.safe_get(post, ["tableOfContents", "sections"])[-1]["title"] + '</h2>\n'
    else:
        result += '''<h2 id="comments">''' + str(post['commentCount']) + ' comments</h2>'

    # map of commentId -> list of commentIds that have replied
    reply_graph: dict[str, list[str]] = {}
    for comment in comments:
        commentid = util.safe_get(comment, ['_id'])
        parentid = util.safe_get(comment, ['parentCommentId'])
        if parentid:
            if parentid in reply_graph:
                reply_graph[parentid].append(commentid)
            else:
                reply_graph[parentid] = [commentid]

    for comment in comments:
        color = config.COMMENT_COLOR
        commentid = comment['_id']
        result += "<div>"  # this extra outer div will ensure that two very short comments aren't displayed side-by-side
        result += ('''<div id="%s" style="border: 1px solid #B3B3B3; padding-left: 15px; padding-right: 15px; padding-bottom: 10px; padding-top: 10px; margin-left: 0px; margin-right: -1px; margin-bottom: 0px; margin-top: 10px; background-color: %s; display: inline-block;">''' % (commentid, color))
        result += '<span style="color: #117743; font-weight: 700;">Anonymous</span> '
        result += " ·\n"
        result += (('''<a href="#%s">''' % commentid) + comment['postedAt'] + "</a> · ")
        if "lesswrong" in config.GRAPHQL_URL:
            result += ('<a title="Official LessWrong 2.0 link" href="' + comment['pageUrl'] + '">LW</a> · ')
        else:
            result += ('<a title="Official EA Forum link" href="' + comment['pageUrl'] + '">EA</a> · ')
        result += '<a title="GreaterWrong link" href="' + util.official_url_to_gw(comment['pageUrl']) + '">GW</a>'
        # This comment has replies, so show their IDs
        if commentid in reply_graph:
            for reply in reply_graph[commentid]:
                result += ''' <a href="#%s" onmouseover="showComment(this, '%s')" onmouseout="removeComment('%s')">&gt;&gt;%s</a>''' % (reply, reply, reply, reply)
        result += '<br/>'
        if util.safe_get(comment, ['parentCommentId']):
            result += '''<br/><a href="#%s" id="%s" class="reply-parent" onmouseover="showComment(this, '%s')" onmouseout="removeComment('%s')">&gt;&gt;%s</a><br/>''' % (
                    util.safe_get(comment, ['parentCommentId']),
                    util.safe_get(comment, ['parentCommentId']),
                    util.safe_get(comment, ['parentCommentId']),
                    util.safe_get(comment, ['parentCommentId']),
                    util.safe_get(comment, ['parentCommentId'])
                    )
        result += util.cleanHtmlBody(util.substitute_alt_links(comment['htmlBody']))
        result += "</div></div>"

    result += ("""
    </div>
    </div>

        <script>
            function showComment(pointer, commentid) {
                var comment = document.getElementById(commentid);
                var clone = comment.cloneNode(true);
                var rect = pointer.getBoundingClientRect();

                clone.id = "cloned-" + commentid;
                clone.style.position = 'absolute';
                clone.style.top = (window.pageYOffset + rect.top) + 'px';
                if (window.innerWidth - rect.right < 100) {
                    clone.style.right = rect.left + 'px';
                } else {
                    clone.style.left = rect.right + 'px';
                }
                document.body.appendChild(clone);
            }
            function removeComment(commentid) {
                var clone = document.getElementById("cloned-" + commentid);
                clone.parentNode.removeChild(clone);
            }
        </script>

        </body>
        </html>
    """)

    return result

if __name__ == "__main__":
    if len(sys.argv) != 2 + 1:
        print("Please enter a post ID as argument")
    else:
        print(show_post_and_comment_thread(postid=sys.argv[1], display_format=sys.argv[2]))

