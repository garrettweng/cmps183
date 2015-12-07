# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

from gluon import utils as gluon_utils
import json
import time


def index():
    team_list = db().select(db.team.ALL)
    user_id = auth.user_id
    user_team = db(db.team.user_id == user_id).select(db.team.ALL).first()
    user_has_team = user_team is not None
    return dict(user_id=user_id, team_list=team_list,user_team=user_team, user_has_team=user_has_team)

@auth.requires_login()
@auth.requires_signature()
def newteam():
    form = SQLFORM(db.team)
    if form.process().accepted:
        response.flash = 'Team Created!'
        redirect(URL('default', 'index'))
    elif form.errors:
        response.flash = "Team name cannot be empty"
    return dict(form=form)


@auth.requires_login()
@auth.requires_signature()
def newplayer():
    form = SQLFORM(db.player)
    if form.process().accepted:
        response.flash = 'Player Added!'
        redirect(URL('default', 'index'))
    elif form.errors:
        response.flash = "Player name and position cannot be empty"
    return dict(form=form)


def team():
    user_team = db(db.team.id == request.args(0)).select(db.team.ALL).first()
    player_list = db(db.player.team == user_team).select(db.player.ALL)
    return dict(user_team=user_team, player_list=player_list)


def players():
    player_list = db().select(db.player.ALL)
    return dict(player_list=player_list)


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


