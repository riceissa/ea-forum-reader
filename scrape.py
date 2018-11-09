#!/usr/bin/env python3

import requests

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

    request = requests.get('https://forum.effectivealtruism.org/graphql', params={'query': query})

    return request.json()['data']['user']['result']['_id']

get_userid("carl_shulman")
