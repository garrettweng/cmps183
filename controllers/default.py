# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

from gluon import utils as gluon_utils
import json
import time


def index():
    user_id = auth.user_id
    return dict(user_id=user_id)


def board():
    board_id = request.args(0)
    user_id = auth.user_id
    return dict(board_id=board_id, userid=user_id)


@auth.requires_login()
def add_board():
    db.board.insert(board_name=request.vars.board_name)
    return "ok"


@auth.requires_login()
def add_post():
    db.post.update_or_insert((db.post.post_id == request.vars.post_id),
                              board=request.args(0),
                              post_id=request.vars.post_id,
                              post_name=request.vars.post_name,
                              post_message=request.vars.post_message)
    return "ok"


@auth.requires_login()
def delete_post():
    print("hello")
    db(db.post.post_id == request.vars.post_id).delete()
    return "ok"


def load_boards():
    """Loads all boards."""
    board_list = db().select(db.board.ALL, orderby=~db.board.id)
    return response.json(dict(board_list=board_list))


def load_posts():
    """Loads posts for a given board"""
    board_id = request.args(0)
    post_list = db(db.post.board == board_id).select(db.post.ALL, orderby=~db.post.id)
    return response.json(dict(post_list=post_list))


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


