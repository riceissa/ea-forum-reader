#!/usr/bin/env python3

import config

PATH_STYLE = config.PATH_STYLE


def posts(postid, postslug="", display_format="html"):
    if PATH_STYLE == "localhost":
        if display_format == "html":
            return "./posts.php?id=" + postid
        else:
            return "./posts.php?id=" + postid + "&amp;format=" + display_format
    else:
        if display_format == "html":
            return "/posts/" + postid + "/" + postslug
        else:
            return "/posts/" + postid + "/" + postslug + "?format=" + display_format

def users(userslug, display_format="html"):
    if PATH_STYLE == "localhost":
        return "./users.php?id=" + userslug + ("&amp;format=" + display_format if display_format != "html" else "")
    else:
        return "/users/" + userslug + ("?format=" + display_format if display_format != "html" else "")

def userlist(sort="karma", display_format="html"):
    if PATH_STYLE == "localhost":
        if display_format != "html":
            return "./userlist.php?sort=" + sort + "&amp;format=" + display_format
        else:
            return "./userlist.php?sort=" + sort
    else:
        if display_format != "html":
            return "/userlist?sort=" + sort + "&amp;format=" + display_format
        else:
            return "/userlist?sort=" + sort

def search():
    if PATH_STYLE == "localhost":
        return "./search.php"
    else:
        return "/search.php"
