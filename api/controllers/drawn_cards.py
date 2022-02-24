import logging, traceback

from api.models.game import Game as game_db
from api.models.players import Players as players_db
from api.models.drawn_cards import DrawnCards as drawn_cards_db

import api.responses as responses

from api.validation import query


def get_drawn_cards(game_uuid, player_uuid, sort_order, order_by, limit, offset):
    try:
        game = game_db.query.get(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        player = players_db.query.get(player_uuid)  # get player from database

        if not player:  # check if player does not exist
            return responses.not_found("player")

        default_sort_order = 'asc'
        default_order_by = 'name'
        default_limit = 0
        default_offset = 0

        invalid_query = query.validate_query(sort_order, order_by, limit, offset, ['name'])

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

        if default_order_by == 'name':
            sort = drawn_cards_db.name

        if default_sort_order == 'asc':
            sort = sort.asc()
        elif default_sort_order == 'desc':
            sort = sort.desc()

        if default_limit == 0:
            cards = drawn_cards_db.query.filter_by(player_uuid=player_uuid).order_by(sort).offset(default_offset).all()
        else:
            cards = drawn_cards_db.query.filter_by(player_uuid=player_uuid).order_by(sort).limit(default_limit).offset(default_offset).all()

        return responses.success_get_cards(cards)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()
