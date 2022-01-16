import logging, traceback, random

from api.classes.card import *
from api.classes.game import *
from api.classes.player import *

from api.models.characters import Characters as characters_db
from api.models.game import Game as game_db
from api.models.players import Players as players_db
from api.models.deck_characters import DeckCharacters as deck_characters_db
from api.models.possible_characters import PossibleCharacters as possible_characters_db
from api.models.removed_characters import RemovedCharacters as removed_characters_db

import api.responses as responses

from api.services import database

from api.utils import helpers

from api.validation import query

from pprint import pprint


def get_players(game_uuid, sort_order, order_by, limit, offset):
    try:
        game = game_db.query.get(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

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
            sort = players_db.created
        elif default_order_by == 'name':
            sort = players_db.name

        if default_sort_order == 'asc':
            sort = sort.asc()
        elif default_sort_order == 'desc':
            sort = sort.desc()

        if default_limit == 0:
            players = players_db.query.filter_by(game_uuid=game_uuid).order_by(sort).offset(default_offset).all()
        else:
            players = players_db.query.filter_by(game_uuid=game_uuid).order_by(sort).limit(default_limit).offset(default_offset).all()

        return responses.success_get_players(players)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def get_player(game_uuid, player_uuid):
    try:
        game = game_db.query.get(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        player = players_db.query.get(player_uuid)

        if player:
            return responses.success_get_player(player)

        return responses.not_found()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def select_character(game_uuid, player_uuid, name):
    try:
        game = game_db.query.get(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        game = ClassGame(database_object=game)  # initialize game object

        if game.state != ClassState.selection_phase.value:  # check if game is in selection phase
            return responses.not_selection_phase()

        player = players_db.query.get(player_uuid)  # get player from database

        if not player:  # check if player does not exist
            return responses.not_found("player")

        if not player.select_expected:  # check if player needs to select character
            return responses.not_select_expected()

        game.players.append(ClassPlayer(database_object=player))  # add player to game object

        character_possible = False

        possible_characters = possible_characters_db.query.filter_by(game_uuid=game_uuid).all()  # get possible characters in game

        if possible_characters:  # check if there are possible characters
            character = list(filter(lambda character: character.name == name, possible_characters))  # get character

            if character:  # check if there is a character with the given name
                character_possible = True  # character is in game

        if not character_possible:  # check if character is not possible
            return responses.not_found("character")

        game.possible_characters = list(map(lambda character: ClassCharacter(database_object=character), possible_characters))  # add deck of possible characters to game object

        removed_characters = removed_characters_db.query.filter_by(game_uuid=game_uuid).all()  # get removed characters in game

        game.removed_characters = list(map(lambda character: ClassCharacter(database_object=character), removed_characters))  # add deck of removed characters to game object

        game.set_character(name)  # add character to player's hands and remove it from possible characters

        success_write_character = database.write_row_to_db(characters_db(  # write character to database
            uuid=helpers.create_uuid(),
            name=game.players[0].character[0].name,
            open=game.players[0].character[0].open,
            assassinated=game.players[0].character[0].assassinated,
            robbed=game.players[0].character[0].robbed,
            built=game.players[0].character[0].built,
            player_uuid=player_uuid))

        if not success_write_character:  # check if failed to write to database
            return responses.error_writing_database("character")

        success_delete_possible_character = database.delete_row_from_db(possible_characters_db, game.players[0].character[0].uuid)  # delete character from possible characters in database

        if not success_delete_possible_character:  # check if failed to delete in database
            return responses.error_deleting_database("possible character")

        success_update_player = database.update_row_in_db(players_db, player_uuid, dict(select_expected=False))  # update select expected flag for current player in database

        if not success_update_player:  # check if failed to update database
            return responses.error_updating_database("player")

        selection_phase_finished = True

        selected_characters_count = 0

        players = players_db.query.filter_by(game_uuid=game_uuid).all()  # get players in game

        if not players:  # check if player does not exist
            return responses.not_found("players", True)

        players = list(map(lambda player: ClassPlayer(database_object=player), players))  # initialize player objects | don't add to game object because it messes with how the next seat is calculated

        for player in players:  # go through each player
            characters = characters_db.query.filter_by(player_uuid=player.uuid).all()  # get characters in player's hands

            if len(characters) != game.characters_per_player:  # check if player does not have the expected amount of characters
                selection_phase_finished = False

            selected_characters_count += len(characters)  # keep track of how many characters have already been selected

        if selection_phase_finished:  # check if the selection phase is finished
            # TODO: add logic to set expected turn flag for required player

            for character in game.possible_characters:  # go through remaining possible characters
                success_write_removed_character = database.write_row_to_db(removed_characters_db(  # write character to database
                    uuid=helpers.create_uuid(),
                    name=character.name,
                    open=character.open,
                    assassinated=character.assassinated,
                    robbed=character.robbed,
                    built=character.built,
                    game_uuid=game_uuid))

                if not success_write_removed_character:  # check if failed to write to database
                    return responses.error_writing_database("removed character")

                success_delete_possible_character = database.delete_row_from_db(possible_characters_db, character.uuid)  # delete character from possible characters in database

                if not success_delete_possible_character:  # check if failed to delete in database
                    return responses.error_deleting_database("possible character")

            game.state = ClassState.turn_phase.value  # update game to say it is ready to let each character perform their turn

            success_update_game = database.update_row_in_db(game_db, game_uuid, dict(state=game.state))  # update database with the latest information about the game state

            if not success_update_game:  # check if database failed to update
                return responses.error_updating_database("game")

        else:  # there are players who still need to select characters
            next_seat_select_expected = game.players[0].seat + 1  # decide which player needs to pick a character next

            if next_seat_select_expected == game.amount_players:  # check if limit reached
                next_seat_select_expected = 0  # start back from seat 0

            player = players_db.query.filter_by(game_uuid=game_uuid, seat=next_seat_select_expected).first()  # get player in game who is expected to pick next

            if not player:  # check if player does not exist
                return responses.not_found("player")

            player_uuid = player.uuid  # get uuid of the next player | get value now before connection with database closes

            success_update_player = database.update_row_in_db(players_db, player_uuid, dict(select_expected=True))  # update select expected flag for next player in database

            if not success_update_player:  # check if failed to update database
                return responses.error_updating_database("player")

            if selected_characters_count == 6:  # check if player 7 needs to pick a character next | when game has 7 players, player 7 can pick between the removed facedown card and the possible character
                characters = list(filter(lambda character: character.open == False, game.removed_characters))  # get facedown removed characters

                for character in characters:  # go through characters
                    success_write_possible_character = database.write_row_to_db(possible_characters_db(  # write character to database
                        uuid=helpers.create_uuid(),
                        name=character.name,
                        open=character.open,
                        assassinated=character.assassinated,
                        robbed=character.robbed,
                        built=character.built,
                        game_uuid=game_uuid))

                    if not success_write_possible_character:  # check if failed to write to database
                        return responses.error_writing_database("possible character")

                    success_delete_possible_character = database.delete_row_from_db(removed_characters_db, character.uuid)  # delete character from possible characters in database

                    if not success_delete_possible_character:  # check if failed to delete in database
                        return responses.error_deleting_database("removed character")

        return responses.no_content()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()
