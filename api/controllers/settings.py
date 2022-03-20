import logging, traceback

from api.models.settings import Settings as settings_db

import api.responses as responses

from api.utils import transactions

from api.validation import query


def get_settings(game_uuid, sort_order, order_by, limit, offset):
    try:
        game = transactions.get_game(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        invalid_query = query.validate_query(sort_order, order_by, limit, offset, ['uuid'])  # validate query parameters

        if invalid_query:  # check if invalid query
            return responses.conflict(invalid_query)

        settings = transactions.get_all_from_query(settings_db, sort_order, order_by, limit, offset, uuid=game_uuid, default_order_by="uuid")  # get all from database based on query

        return responses.success_get_settings(settings)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()
