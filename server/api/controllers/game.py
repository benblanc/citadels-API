import logging, traceback

from api.classes import card, game, player

from api.models.game import Game as game_db
from api.models.settings import Settings as settings_db
from api.models.deck_districts import DeckDistricts as deck_districts_db
from api.models.deck_characters import DeckCharacters as deck_characters_db
from api.models.players import Players as players_db

import api.responses as responses

from api.services import database

from api.utils import helpers

from api.validation import query

from pprint import pprint


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

        return responses.db_success_reading_all_games(games)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.internal_server_error()


def get_game(game_uuid):
    try:
        game = game_db.query.get(game_uuid)

        if game:
            return responses.db_success_reading_game(game)

        return responses.not_found()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.internal_server_error()


def create_game(name, description):
    try:
        new_game = game.ClassGame(helpers.create_uuid(), helpers.create_timestamp(), name, description)

        success_write_game = database.write_row_to_db(game_db(
            uuid=new_game.uuid,
            created=new_game.created,
            name=new_game.name,
            description=new_game.description,
            started=new_game.started,
            amount_players=new_game.amount_players,
            characters_unused=new_game.characters_unused,
            characters_per_player=new_game.characters_per_player,
            eight_districts_built=new_game.eight_districts_built,
            round=new_game.round))

        if not success_write_game:
            return responses.internal_server_error()

        success_write_settings = database.write_row_to_db(settings_db(
            uuid=helpers.create_uuid(),
            min_players=new_game.settings.min_players,
            max_players=new_game.settings.max_players,
            amount_starting_hand=new_game.settings.amount_starting_hand,
            amount_starting_coins=new_game.settings.amount_starting_coins,
            game_uuid=new_game.uuid))

        if not success_write_settings:
            return responses.internal_server_error()

        new_game.deck_districts = card.ClassCard().get_districts(False)

        success_write_deck_districts = []
        for district in new_game.deck_districts:
            success_write_deck_districts.append(database.write_row_to_db(deck_districts_db(
                uuid=helpers.create_uuid(),
                name=district.card.name,
                amount=district.amount,
                game_uuid=new_game.uuid)))

        if False in success_write_deck_districts:
            return responses.internal_server_error()

        new_game.deck_characters = card.ClassCard().get_characters()

        success_write_deck_characters = []
        for character in new_game.deck_characters:
            success_write_deck_characters.append(database.write_row_to_db(deck_characters_db(
                uuid=helpers.create_uuid(),
                name=character.name,
                game_uuid=new_game.uuid)))

        return responses.success_uuid_entity_created(new_game.uuid)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.internal_server_error()


def join_game(game_uuid, name):
    try:
        game = game_db.query.get(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found()

        game_uuid = game.uuid  # get game uuid before connection with database closes

        # TODO: add check to see if player amount does not exceed max_players defined in settings linked to game through uuid

        hosting = True  # assume new player is hosting

        players = players_db.query.filter_by(game_uuid=game_uuid).all()  # get players in game

        if players:  # check if there are players
            host = list(filter(lambda player: player.hosting == True, players))  # get host

            if host:  # check if there is a host
                hosting = False  # new player will not host the game

        new_player = player.ClassPlayer(helpers.create_uuid(), name, hosting)

        success_write_player = database.write_row_to_db(players_db(
            uuid=new_player.uuid,
            name=new_player.name,
            hosting=new_player.hosting,
            index=new_player.index,
            coins=new_player.coins,
            flag_king=new_player.flag_king,
            flag_assassinated=new_player.flag_assassinated,
            flag_robbed=new_player.flag_robbed,
            flag_protected=new_player.flag_protected,
            flag_built=new_player.flag_built,
            game_uuid=game_uuid
        ))

        if not success_write_player:
            return responses.internal_server_error()

        success_update_game = database.update_row_from_db(game_db, game_uuid, dict(amount_players=len(players) + 1))  # update player count for game

        if not success_update_game:
            return responses.internal_server_error()

        return responses.success_uuid_entity_created(new_player.uuid)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.internal_server_error()


def start_game(game_uuid, player_uuid):
    try:
        game = game_db.query.get(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found()

        game_uuid = game.uuid  # get game uuid before connection with database closes

        amount_players = game.amount_players  # get amount of players in game before connection with database closes

        player = players_db.query.get(player_uuid)  # get player from database

        if not player:  # check if player does not exist
            return responses.not_found()

        if not player.hosting:  # check if the player is not hosting the game
            return responses.not_host()

        settings = settings_db.query.filter_by(game_uuid=game_uuid).first()  # get settings from database

        if amount_players < settings.min_players:  # check if there are not enough players
            return responses.not_enough_players()

        success_update_game = database.update_row_from_db(game_db, game_uuid, dict(started=True))  # update game to say it has started

        if not success_update_game:  # check if database failed to update
            return responses.internal_server_error()

        ### game has started
        ## prepare game



        return responses.no_content()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.internal_server_error()
