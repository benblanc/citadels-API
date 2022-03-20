import logging, traceback

from api.models.deck_discard_pile import DeckDiscardPile as deck_discard_pile_db

import api.responses as responses

from api.utils import transactions

from api.validation import query


def get_deck_discard_pile(game_uuid, sort_order, order_by, limit, offset):
    try:
        game = transactions.get_game(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        invalid_query = query.validate_query(sort_order, order_by, limit, offset, ['name'])  # validate query parameters

        if invalid_query:  # check if invalid query
            return responses.conflict(invalid_query)

        districts = transactions.get_all_from_query(deck_discard_pile_db, sort_order, order_by, limit, offset, uuid=game_uuid)  # get all from database based on query

        return responses.success_get_districts(districts)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()
