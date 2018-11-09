#!/usr/bin/env python3

import requests

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
    pass


def get_comments_for_user(username):
    pass


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

get_userid("carl_shulman")
