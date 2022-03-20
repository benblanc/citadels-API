import logging, traceback

from api.models.characters import Characters as characters_db

import api.responses as responses

from api.utils import transactions

from api.validation import query


def get_characters(game_uuid, player_uuid, sort_order, order_by, limit, offset):
    try:
        game = transactions.get_game(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        player = transactions.get_player(player_uuid)  # get player from database

        if not player:  # check if player does not exist
            return responses.not_found("player")

        invalid_query = query.validate_query(sort_order, order_by, limit, offset, ['name'])  # validate query parameters

        if invalid_query:  # check if invalid query
            return responses.conflict(invalid_query)

        characters = transactions.get_all_from_query(characters_db, sort_order, order_by, limit, offset, uuid=player_uuid, player_table=True)  # get all from database based on query

        return responses.success_get_characters(characters)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()
