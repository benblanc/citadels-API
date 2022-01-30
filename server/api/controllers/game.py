import logging, traceback

from api.classes.card import *
from api.classes.game import *
from api.classes.player import *

from api.models.game import Game as game_db
from api.models.settings import Settings as settings_db
from api.models.deck_districts import DeckDistricts as deck_districts_db
from api.models.deck_characters import DeckCharacters as deck_characters_db
from api.models.players import Players as players_db

import api.responses as responses

from api.services import database

from api.utils import helpers

from api.validation import query


def get_games(sort_order, order_by, limit, offset):
    try:
        default_sort_order = 'asc'
        default_order_by = 'created'
        default_limit = 0
        default_offset = 0

        invalid_query = query.validate_query(sort_order, order_by, limit, offset, ['created', 'name'])

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
        elif default_order_by == 'name':
            sort = game_db.name

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


def create_game(name, description):
    try:
        new_game = ClassGame(helpers.create_uuid(), helpers.create_timestamp(), name, description, ClassState.created.value)

        success_write_game = database.write_row_to_db(game_db(
            uuid=new_game.uuid,
            created=new_game.created,
            name=new_game.name,
            description=new_game.description,
            state=new_game.state,
            amount_players=new_game.amount_players,
            characters_open=new_game.characters_open,
            characters_closed=new_game.characters_closed,
            characters_per_player=new_game.characters_per_player,
            eight_districts_built=new_game.eight_districts_built,
            character_turn=new_game.character_turn,
            round=new_game.round))

        if not success_write_game:
            return responses.error_writing_database("game")

        success_write_settings = database.write_row_to_db(settings_db(
            uuid=helpers.create_uuid(),
            min_players=new_game.settings.min_players,
            max_players=new_game.settings.max_players,
            amount_starting_hand=new_game.settings.amount_starting_hand,
            amount_starting_coins=new_game.settings.amount_starting_coins,
            game_uuid=new_game.uuid))

        if not success_write_settings:
            return responses.error_writing_database("settings")

        new_game.deck_districts = ClassCard().get_districts(False)

        success_write_deck_districts = []
        for district in new_game.deck_districts:
            success_write_deck_districts.append(database.write_row_to_db(deck_districts_db(
                uuid=helpers.create_uuid(),
                name=district.card.name,
                amount=district.amount,
                game_uuid=new_game.uuid)))

        if False in success_write_deck_districts:
            return responses.error_writing_database("deck of districts")

        new_game.deck_characters = ClassCard().get_characters()

        success_write_deck_characters = []
        for character in new_game.deck_characters:
            success_write_deck_characters.append(database.write_row_to_db(deck_characters_db(
                uuid=helpers.create_uuid(),
                name=character.name,
                open=character.open,
                assassinated=character.assassinated,
                robbed=character.robbed,
                built=character.built,
                income_received=character.income_received,
                game_uuid=new_game.uuid)))

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
            host = list(filter(lambda player: player.hosting == True, players))  # get host

            if host:  # check if there is a host
                hosting = False  # new player will not host the game

        new_player = ClassPlayer(helpers.create_uuid(), helpers.create_timestamp(), name, hosting)

        success_write_player = database.write_row_to_db(players_db(
            uuid=new_player.uuid,
            created=new_player.created,
            name=new_player.name,
            hosting=new_player.hosting,
            seat=new_player.seat,
            coins=new_player.coins,
            king=new_player.king,
            protected=new_player.protected,
            select_expected=new_player.select_expected,
            game_uuid=game_uuid
        ))

        if not success_write_player:
            return responses.error_writing_database("player")

        success_update_game = database.update_row_in_db(game_db, game_uuid, dict(amount_players=len(players) + 1))  # update player count for game

        if not success_update_game:
            return responses.error_updating_database("game")

        return responses.success_uuid(new_player.uuid)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()
