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
            sort = deck_discard_pile_db.name

        if default_sort_order == 'asc':
            sort = sort.asc()
        elif default_sort_order == 'desc':
            sort = sort.desc()

        if default_limit == 0:
            districts = deck_discard_pile_db.query.filter_by(game_uuid=game_uuid).order_by(sort).offset(default_offset).all()
        else:
            districts = deck_discard_pile_db.query.filter_by(game_uuid=game_uuid).order_by(sort).limit(default_limit).offset(default_offset).all()

        return responses.success_get_districts(districts)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()
