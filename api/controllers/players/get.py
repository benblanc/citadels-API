import logging, traceback

from api.models.players import Players as players_db

import api.responses as responses

from api.utils import transactions

from api.validation import query


def get_players(game_uuid, sort_order, order_by, limit, offset):
    try:
        game = transactions.get_game(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        invalid_query = query.validate_query(sort_order, order_by, limit, offset, ['created', 'name'])  # validate query parameters

        if invalid_query:  # check if invalid query
            return responses.conflict(invalid_query)

        players = transactions.get_all_from_query(players_db, sort_order, order_by, limit, offset, uuid=game_uuid, default_order_by="created")  # get all from database based on query

        return responses.success_get_players(players)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def get_player(game_uuid, player_uuid):
    try:
        game = transactions.get_game(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        player = transactions.get_player(player_uuid)  # get player from database

        if player:  # check if player does not exist
            return responses.success_get_player(player)

        return responses.not_found()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()
