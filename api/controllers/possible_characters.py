import logging, traceback

from api.models.game import Game as game_db
from api.models.possible_characters import PossibleCharacters as possible_characters_db

import api.responses as responses

from api.validation import query


def get_possible_characters(game_uuid, sort_order, order_by, limit, offset):
    try:
        game = game_db.query.get(game_uuid)  # get game from database

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
            sort = possible_characters_db.name

        if default_sort_order == 'asc':
            sort = sort.asc()
        elif default_sort_order == 'desc':
            sort = sort.desc()

        if default_limit == 0:
            characters = possible_characters_db.query.filter_by(game_uuid=game_uuid).order_by(sort).offset(default_offset).all()
        else:
            characters = possible_characters_db.query.filter_by(game_uuid=game_uuid).order_by(sort).limit(default_limit).offset(default_offset).all()

        return responses.success_get_characters(characters)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()
