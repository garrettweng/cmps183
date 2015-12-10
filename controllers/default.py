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
    # calculate current week points for each team
    for team in team_list:
        week_points = 0
        players = db(db.player.team == team.id).select(db.player.ALL)
        for player in players:
            # calculate player points for the week
            player_points = calc_points(player)
            week_points += player_points
        db.team.update_or_insert((db.team.id == team.id),
                                 week_points=week_points)
    # need to get the updated team values
    team_list = db().select(db.team.ALL)
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
def remove_team():
    db(db.team.id == request.args(0)).delete()
    redirect(URL('default', 'index'))
    return


@auth.requires_login()
@auth.requires_signature()
def newplayer():
    form = SQLFORM(db.player)
    if form.process().accepted:
        response.flash = 'Player Added!'
        redirect(URL('default', 'players'))
    elif form.errors:
        response.flash = "Player name and position cannot be empty"
    return dict(form=form)


@auth.requires_login()
@auth.requires_signature()
def draft():
    user_team = db(db.team.user_id == auth.user_id).select().first()
    return dict(team_id=user_team.id)


@auth.requires_login()
@auth.requires_signature()
def load_teams():
    team_list = db().select(db.team.ALL, orderby=db.team.id)
    user_team = db(db.team.user_id == auth.user_id).select().first()
    user_players = db(db.player.team == request.args(0)).select(db.player.ALL, orderby=db.player.id)
    player_list = db().select(db.player.ALL, orderby=~db.player.points)
    turn = db().select(db.draft.ALL).first().turn
    return response.json(dict(team_list=team_list, user_team=user_team, user_players=user_players, player_list=player_list, turn=turn))


@auth.requires_login()
@auth.requires_signature()
def draft_add_team():
    db.team.update_or_insert((db.team.id == request.vars.team_id),
                             ready=True)
    return "ok"


@auth.requires_login()
@auth.requires_signature()
def add_user_player():
    db.team.update_or_insert((db.player.id == request.vars.player_id),
                             team=request.args(0))
    # increment turn
    team_list = db().select(db.team.ALL)
    num_teams = 0
    for team in team_list:
        num_teams += 1

    row = db().select(db.draft.ALL).first()
    next_turn = int(row.turn)
    next_turn = (next_turn + 1) % num_teams
    db.draft.update_or_insert(db.draft.id == row.id,
                              turn=next_turn)
    return "ok"


@auth.requires_login()
@auth.requires_signature()
def draft_remove_team():
    db.team.update_or_insert((db.team.id == request.vars.team_id),
                             ready=False)
    return "ok"


@auth.requires_login()
@auth.requires_signature()
def reset_draft():
    # resets player stats and updates points totals in DB
    team_list = db().select(db.team.ALL)
    for team in team_list:
        total_team_points = int(db.team[team.id].total_points)
        week_points = 0
        players = db(db.player.team == team.id).select(db.player.ALL)
        for player in players:
            # calculate player points for the week
            player_points = calc_points(player)
            week_points += player_points
        # update team total points in DB, and set not ready
        total_team_points += week_points
        db.team.update_or_insert((db.team.id == team.id),
                                 total_points=total_team_points,
                                 ready=False)
    # Now need to update players not on a team
    player_list = db().select(db.player.ALL)
    for player in player_list:
        player_points = calc_points(player)
        total_points = player_points + int(db.player[player.id].points)
        db.player.update_or_insert((db.player.id == player.id),
                                   team=None,
                                   points=total_points,
                                   yards=0,
                                   touchdowns=0,
                                   field_goals=0,
                                   interceptions=0,
                                   fumbles=0)
    # reset the turn counter
    draft_id = db().select(db.draft.ALL).first().id
    db.draft.update_or_insert(db.draft.id == draft_id,
                              turn=0)
    return "ok"


def team():
    user_team = db(db.team.id == request.args(0)).select(db.team.ALL).first()
    player_list = db(db.player.team == user_team).select(db.player.ALL)
    return dict(user_team=user_team, player_list=player_list)


def players():
    player_list = db().select(db.player.ALL)
    points_list = []
    for p in player_list:
        points_list.append(calc_points(p))
    return dict(player_list=player_list, points_list=points_list)


def calc_points(player):
    points = (int(player.yards) / 10) + (int(player.touchdowns) * 5) + (int(player.field_goals) * 3) - (int(player.interceptions) * 2) - (int(player.fumbles) * 2)
    return points


def edit_stats():
    switch_true()
    record = db.player(request.args(0)) or redirect(URL('default', 'index'))
    form = SQLFORM(db.player, record)
    if form.process().accepted:
        response.flash = "Stats posted!"
        redirect(URL('default', 'players'))
    elif form.errors:
        response.flash = "Stat fields cannot be empty"
    switch_false()
    return dict(form=form)

def switch_true():
    db.player.name.readable = db.player.name.writable = False
    db.player.pos.readable = db.player.pos.writable = False
    db.player.team.readable = db.player.team.writable = False
    db.player.yards.readable = db.player.yards.writable = True
    db.player.touchdowns.readable = db.player.touchdowns.writable = True
    db.player.field_goals.readable = db.player.field_goals.writable = True
    db.player.interceptions.readable = db.player.interceptions.writable = True
    db.player.fumbles.readable = db.player.fumbles.writable = True
    return


def switch_false():
    db.player.name.readable = db.player.name.writable = True
    db.player.pos.readable = db.player.pos.writable = True
    db.player.team.readable = db.player.team.writable = True
    db.player.yards.readable = db.player.yards.writable = False
    db.player.touchdowns.readable = db.player.touchdowns.writable = False
    db.player.field_goals.readable = db.player.field_goals.writable = False
    db.player.interceptions.readable = db.player.interceptions.writable = False
    db.player.fumbles.readable = db.player.fumbles.writable = False
    return


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


