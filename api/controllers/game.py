import logging, traceback

from api.classes.card import *
from api.classes.game import *
from api.classes.player import *

from api.models.game import Game as game_db

import api.responses as responses

from api.services import database

from api.utils import helpers, transactions

from api.validation import query


def get_games(sort_order, order_by, limit, offset):
    try:
        invalid_query = query.validate_query(sort_order, order_by, limit, offset, ['created'])  # validate query parameters

        if invalid_query:  # check if invalid query
            return responses.conflict(invalid_query)

        games = transactions.get_all_from_query(game_db, sort_order, order_by, limit, offset, default_order_by="created")  # get all from database based on query

        return responses.success_get_games(games)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def get_game(game_uuid):
    try:
        game = transactions.get_game(game_uuid)  # get game from database

        if game:  # check if game exists
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

        new_game.deck_districts = ClassCard().get_districts()  # get districts in game

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
        game = transactions.get_game(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        if game.state != ClassState.created.value:  # check if game has already started
            return responses.already_started()

        settings = transactions.get_game_settings(game_uuid)  # get settings from database

        if not settings:  # check if game settings do not exist
            return responses.not_found("settings", True)

        game.settings = settings  # add settings to game object

        if game.amount_players == game.settings.max_players:  # check if there are already enough players
            return responses.enough_players()

        hosting = True  # assume new player is hosting

        players = transactions.get_players(game_uuid)  # get players in game

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
