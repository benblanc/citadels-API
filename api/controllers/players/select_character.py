import logging, traceback

from api.classes.card import *
from api.classes.game import *

from api.models.characters import Characters as characters_db
from api.models.game import Game as game_db
from api.models.players import Players as players_db
from api.models.possible_characters import PossibleCharacters as possible_characters_db
from api.models.removed_characters import RemovedCharacters as removed_characters_db

import api.responses as responses

from api.services import database

from api.utils import helpers, transactions


def select_character(game_uuid, player_uuid, name, remove):
    try:
        game = transactions.get_game(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        if game.state != ClassState.selection_phase.value:  # check if game is in selection phase
            return responses.not_selection_phase()

        game.set_character_division()  # define how many characters per player and how many are open or closed on the field

        player = transactions.get_player(player_uuid)  # get player from database

        if not player:  # check if player does not exist
            return responses.not_found("player")

        if not player.select_expected:  # check if player needs to select character
            return responses.not_select_expected()

        game.players.append(player)  # add player to game object

        character_possible = False

        possible_characters = transactions.get_game_possible_characters(game_uuid)  # get possible characters in game

        if possible_characters:  # check if there are possible characters
            character = helpers.get_filtered_item(possible_characters, "name", name)  # get character

            if character:  # check if there is a character with the given name
                character_possible = True  # character is in game

        if not character_possible:  # check if character cannot be picked
            return responses.not_found("character")

        game.possible_characters = possible_characters  # add deck of possible characters to game object

        game.removed_characters = transactions.get_game_removed_characters(game_uuid)  # get removed characters in game

        remove_character_possible = False  # outside the if structure where it's used so it can also be used to determine log text

        if possible_characters and game.amount_players == 2 and len(game.removed_characters) > 1 or possible_characters and game.amount_players == 2 and not game.players[0].king:  # check if there are possible characters, two player game and atleast 2 removed characters or if there are possible characters, two player game and it's not the first player
            remove_character = helpers.get_filtered_item(possible_characters, "name", remove)  # get character to remove

            if remove_character:  # check if there is a character with given name
                remove_character_possible = True  # character is in game

            if not remove_character_possible:  # check if character cannot be removed
                return responses.not_found("remove character")

            if name == remove:  # check if character to pick is same as character to remove
                return responses.same_character()

        character = game.remove_character_from_possible_characters(name)  # remove character from possible characters for round

        success_write_character = transactions.write_character_to_player_characters(player_uuid, character)  # write character to database

        if not success_write_character:  # check if failed to write to database
            return responses.error_writing_database("character")

        success_delete_possible_character = database.delete_row_from_db(possible_characters_db, character.uuid)  # delete character from possible characters in database

        if not success_delete_possible_character:  # check if failed to delete in database
            return responses.error_deleting_database("possible character")

        if game.amount_players == 2 and len(game.removed_characters) > 1 or game.amount_players == 2 and not game.players[0].king:  # check if game has only 2 players and atleast 2 characters have been removed | game with 2 players requires each player to also remove a character for the round, where player two gets to remove the first character
            character = game.remove_character_from_possible_characters(remove)  # remove character from possible characters for round

            success_write_character = transactions.write_character_to_removed_characters(game_uuid, character)  # write character to database

            if not success_write_character:  # check if failed to write to database
                return responses.error_writing_database("character")

            success_delete_possible_character = database.delete_row_from_db(possible_characters_db, character.uuid)  # delete character from possible characters in database

            if not success_delete_possible_character:  # check if failed to delete in database
                return responses.error_deleting_database("possible character")

        success_update_player = database.update_row_in_db(players_db, player_uuid, dict(select_expected=False))  # update select expected flag for current player in database

        if not success_update_player:  # check if failed to update database
            return responses.error_updating_database("player")

        log = "{player_name} picked a character.\n".format(player_name=game.players[0].name)  # update log

        if remove_character_possible:  # check if removing the character with provided name is possible
            log = "{player_name} picked a character and removed a character.\n".format(player_name=game.players[0].name)  # update log

        selection_phase_finished = True

        selected_characters_count = 0

        players = transactions.get_players(game_uuid)  # get players in game

        if not players:  # check if player does not exist
            return responses.not_found("players", True)

        for player in players:  # go through each player
            characters = transactions.get_player_characters(player.uuid)  # get characters in player's hand

            if len(characters) != game.characters_per_player:  # check if player does not have the expected amount of characters
                selection_phase_finished = False

            selected_characters_count += len(characters)  # keep track of how many characters have already been selected

        if selection_phase_finished:  # check if the selection phase is finished
            for character in game.possible_characters:  # go through remaining possible characters
                success_write_removed_character = transactions.write_character_to_removed_characters(game_uuid, character)  # write character to database

                if not success_write_removed_character:  # check if failed to write to database
                    return responses.error_writing_database("removed character")

                success_delete_possible_character = database.delete_row_from_db(possible_characters_db, character.uuid)  # delete character from possible characters in database

                if not success_delete_possible_character:  # check if failed to delete in database
                    return responses.error_deleting_database("possible character")

            game.state = ClassState.turn_phase.value  # update game to say it is ready to let each character perform their turn

            log += "Each player has selected their character(s), so the character turns are up next.\n"  # update log

            characters_complete_info = ClassCard().get_characters()  # get characters in game with complete information

            lowest_character = ClassCharacter(order=8, name=ClassCharacterName.warlord.value)  # keep track of character with the lowest order | start from the highest order number and work the way down

            for player in players:  # go through each player
                characters = transactions.get_player_characters(player.uuid)  # get characters in player's hand

                for character in characters:  # go through player's characters
                    character_complete_info = helpers.get_filtered_item(characters_complete_info, "name", character.name)  # get complete info on character

                    if character_complete_info.order < lowest_character.order:  # check if player's character has a lower order than the current lowest order
                        lowest_character = character_complete_info  # update the lowest character

            log += "The {character_name} is up first.\n".format(character_name=lowest_character.name)  # update log

            game.log += log  # update log

            success_update_game = database.update_row_in_db(game_db, game_uuid, dict(state=game.state, character_turn=lowest_character.name, log=game.log))  # update database with the latest information about the game state

            if not success_update_game:  # check if database failed to update
                return responses.error_updating_database("game")

            for player in players:  # go through each player
                characters = transactions.get_player_characters(player.uuid)  # get characters in player's hand

                for character in characters:  # go through player's characters
                    if character.name == lowest_character.name:  # check if player's character is the first character in the next round to play a turn
                        success_update_character = database.update_row_in_db(characters_db, character.uuid, dict(open=True))  # update open flag for character in database

                        if not success_update_character:  # check if failed to update database
                            return responses.error_updating_database("character")

        else:  # there are players who still need to select characters
            next_seat_select_expected = game.players[0].seat + 1  # decide which player needs to pick a character next

            if next_seat_select_expected == game.amount_players:  # check if limit reached
                next_seat_select_expected = 0  # start back from seat 0

            player = helpers.get_filtered_item(players, "seat", next_seat_select_expected)  # get player in game who is expected to pick next

            if not player:  # check if player does not exist
                return responses.not_found("player")

            log += "{player_name} is up next to pick a character.\n".format(player_name=player.name)  # update log

            # player_uuid = player.uuid  # get uuid of the next player | get value now before connection with database closes

            success_update_player = database.update_row_in_db(players_db, player.uuid, dict(select_expected=True))  # update select expected flag for next player in database

            if not success_update_player:  # check if failed to update database
                return responses.error_updating_database("player")

            if selected_characters_count == 6:  # check if player 7 needs to pick a character next | when game has 7 players, player 7 can pick between the removed facedown card and the possible character
                characters = helpers.get_filtered_items(game.removed_characters, "open", False)  # get facedown removed characters

                for character in characters:  # go through characters
                    success_write_possible_character = transactions.write_character_to_possible_characters(game_uuid, character)  # write character to database

                    if not success_write_possible_character:  # check if failed to write to database
                        return responses.error_writing_database("possible character")

                    success_delete_possible_character = database.delete_row_from_db(removed_characters_db, character.uuid)  # delete character from possible characters in database

                    if not success_delete_possible_character:  # check if failed to delete in database
                        return responses.error_deleting_database("removed character")

            game.log += log  # update log

            success_update_game = database.update_row_in_db(game_db, game_uuid, dict(log=game.log))  # update game log in the database

            if not success_update_game:  # check if database failed to update
                return responses.error_updating_database("game")

        return responses.no_content()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()
