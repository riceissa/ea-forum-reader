#!/usr/bin/env python3

import requests
import json

def send_query(query):
    return requests.get('https://forum.effectivealtruism.org/graphql', params={'query': query})

def get_userid(username):
    query = ("""
    {
      user(input: {selector: {slug: "%s"}}) {
        result {
          _id
        }
      }
    }
    """ % username)

    request = send_query(query)

    return request.json()['data']['user']['result']['_id']


def get_comments_for_post(postid):
    query = ("""
    {
      comments(input: {
        terms: {
          view: "postCommentsTop",
          postId: "%s",
        }
      }) {
        results {
          user {
            _id
            username
            displayName
          }
          userId
          author
          parentCommentId
          pageUrl
          body
          htmlBody
          score
          voteCount
          postedAt
        }
      }
    }
    """ % postid)

    request = send_query(query)
    result = []
    for comment in request.json()['data']['comments']['results']:
        result.append(comment)

    return result

def print_comment_thread(postid):
    comments = get_comments_for_post(postid)

    for comment in comments:
        print("<hr/>")
        print("comment by <b>" + comment['user']['username'] + "</b>,")
        print("<a href=" + '"' + comment['pageUrl'] + '"' + ">" + comment['postedAt'] + "</a>,")
        print("score: " + str(comment['score']) + " (" + str(comment['voteCount']) + " votes)")
        print(comment['htmlBody'])


def get_comments_for_user(username):
    userid = get_userid(username)
    query = ("""
    {
      comments(input: {
        terms: {
          view: "userComments",
          userId: "%s",
        }
      }) {
        results {
          userId
          body
        }
      }
    }
    """ % userid)

    request = send_query(query)
    result = []
    for comment in request.json()['data']['comments']['results']:
        result.append(comment)
    return result


def get_posts_for_user(username):
    userid = get_userid(username)
    query = ("""
    {
      posts(input: {
        terms: {
          view: "userPosts"
          userId: "%s"
          limit: 50
        }
      }) {
        results {
          pageUrl
        }
      }
    }
    """ % userid)

    request = send_query(query)
    result = []
    for post in request.json()['data']['posts']['results']:
        result.append(post['pageUrl'])
    return result

print_comment_thread("NDszJWMsdLCB4MNoy")
