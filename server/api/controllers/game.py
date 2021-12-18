import logging, traceback

from api.classes import card

import api.responses as responses


def get_games(sort_order, limit, offset):
    try:
        return

    except Exception:
        logging.error(traceback.format_exc())
        return responses.internal_server_error()


def get_game(game_uuid):
    try:
        return

    except Exception:
        logging.error(traceback.format_exc())
        return responses.internal_server_error()


def create_game(name, description):
    try:
        return

    except Exception:
        logging.error(traceback.format_exc())
        return responses.internal_server_error()


def join_game(game_uuid):
    try:
        return

    except Exception:
        logging.error(traceback.format_exc())
        return responses.internal_server_error()
