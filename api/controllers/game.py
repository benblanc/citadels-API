import logging, traceback

from api.classes.card import *
from api.classes.game import *
from api.classes.player import *

from api.models.game import Game as game_db
from api.models.players import Players as players_db
from api.models.settings import Settings as settings_db

import api.responses as responses

from api.services import database

from api.utils import helpers, transactions

from api.validation import query


def get_games(sort_order, order_by, limit, offset):
    try:
        default_sort_order = 'asc'
        default_order_by = 'created'
        default_limit = 0
        default_offset = 0

        invalid_query = query.validate_query(sort_order, order_by, limit, offset, ['created'])

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

        if default_order_by == 'created':
            sort = game_db.created

        if default_sort_order == 'asc':
            sort = sort.asc()
        elif default_sort_order == 'desc':
            sort = sort.desc()

        if default_limit == 0:
            games = game_db.query.order_by(sort).offset(default_offset).all()
        else:
            games = game_db.query.order_by(sort).limit(default_limit).offset(default_offset).all()

        return responses.success_get_games(games)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def get_game(game_uuid):
    try:
        game = game_db.query.get(game_uuid)

        if game:
            return responses.success_get_game(game)

        return responses.not_found()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def create_game(description):
    try:
        new_game = ClassGame(helpers.create_uuid(), helpers.create_timestamp(), description, ClassState.created.value, "The host created a game and is now waiting for other players to join.\n")

        success_write_game = transactions.write_game(new_game)  # write game to database

        if not success_write_game:
            return responses.error_writing_database("game")

        success_write_settings = transactions.write_settings(new_game.uuid, new_game.settings)  # write settings to database

        if not success_write_settings:
            return responses.error_writing_database("settings")

        new_game.deck_districts = ClassCard().get_districts(False)  # get districts in game

        success_write_deck_districts = []
        for district in new_game.deck_districts:  # go through districts
            success_write_deck_districts.append(transactions.write_district_to_deck_districts(new_game.uuid, district))  # write district to database

        if False in success_write_deck_districts:
            return responses.error_writing_database("deck of districts")

        new_game.deck_characters = ClassCard().get_characters()  # get characters in game

        success_write_deck_characters = []
        for character in new_game.deck_characters:  # go through characters
            success_write_deck_characters.append(transactions.write_character_to_deck_characters(new_game.uuid, character))  # write character to database

        if False in success_write_deck_characters:
            return responses.error_writing_database("deck of characters")

        return responses.success_uuid(new_game.uuid)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def join_game(game_uuid, name):
    try:
        game = game_db.query.get(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        game = ClassGame(database_object=game)  # initialize game object

        if game.state != ClassState.created.value:  # check if game has already started
            return responses.already_started()

        settings = settings_db.query.filter_by(game_uuid=game_uuid).first()  # get settings from database

        if not settings:  # check if game settings do not exist
            return responses.not_found("settings", True)

        game.settings = ClassSettings(database_object=settings)  # add settings to game object

        if game.amount_players == game.settings.max_players:  # check if there are already enough players
            return responses.enough_players()

        hosting = True  # assume new player is hosting

        players = players_db.query.filter_by(game_uuid=game_uuid).all()  # get players in game

        if players:  # check if there are players
            host = helpers.get_filtered_item(players, "hosting", True)  # get host

            if host:  # check if there is a host
                hosting = False  # new player will not host the game

        new_player = ClassPlayer(helpers.create_uuid(), helpers.create_timestamp(), name, hosting)

        success_write_player = transactions.write_player(game_uuid, new_player)  # write player to database

        if not success_write_player:
            return responses.error_writing_database("player")

        game.log += "{player_name} joined the game.\n".format(player_name=name)  # update game log

        success_update_game = database.update_row_in_db(game_db, game_uuid, dict(amount_players=len(players) + 1, log=game.log))  # update player count and log for game

        if not success_update_game:
            return responses.error_updating_database("game")

        return responses.success_uuid(new_player.uuid)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()
