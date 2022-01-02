import logging, traceback, random

from api.models.game import Game as game_db
from api.models.players import Players as players_db

import api.responses as responses

from api.services import database

from api.utils import helpers

from api.validation import query

from pprint import pprint


def get_players(game_uuid, sort_order, order_by, limit, offset):
    try:
        game = game_db.query.get(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        default_sort_order = 'asc'
        default_order_by = 'index'
        default_limit = 0
        default_offset = 0

        invalid_query = query.validate_query(sort_order, order_by, limit, offset, ['index', 'name'])

        if invalid_query:
            return responses.conflict(invalid_query)

        if sort_order:  # check if not none
            default_sort_order = sort_order

        if order_by:  # check if not none
            default_order_by = order_by

        if limit:  # check if not none
            default_limit = limit

        if offset:  # check if not none
            default_offset = offset

        if default_order_by == 'index':
            sort = players_db.index
        elif default_order_by == 'name':
            sort = players_db.name

        if default_sort_order == 'asc':
            sort = sort.asc()
        elif default_sort_order == 'desc':
            sort = sort.desc()

        if default_limit == 0:
            players = players_db.query.order_by(sort).offset(default_offset).all()
        else:
            players = players_db.query.order_by(sort).limit(default_limit).offset(default_offset).all()

        return responses.success_get_players(players)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def get_player(game_uuid, player_uuid):
    try:
        game = game_db.query.get(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        player = players_db.query.get(player_uuid)

        if player:
            return responses.success_get_player(player)

        return responses.not_found()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()
