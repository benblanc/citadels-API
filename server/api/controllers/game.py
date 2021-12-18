import logging, traceback

from api.classes import game

from api.models.game import Game as game_db

import api.responses as responses

from api.services import database

from api.utils.helpers import *


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
        game_object = game.ClassGame(create_uuid(), create_timestamp(), name, description)

        success_write_game = database.write_row_to_db(game_db(
            uuid=game_object.uuid,
            created=game_object.created,
            name=game_object.name,
            description=game_object.description,
            amount_players=game_object.amount_players,
            characters_unused=game_object.characters_unused,
            characters_per_player=game_object.characters_per_player,
            eight_districts_built=game_object.eight_districts_built,
            round=game_object.round,
        ))

        print(success_write_game)

        return responses.db_success_uuid(game_object.uuid)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.internal_server_error()


def join_game(game_uuid):
    try:
        return

    except Exception:
        logging.error(traceback.format_exc())
        return responses.internal_server_error()
