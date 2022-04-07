import logging, traceback

from api.classes.card import *
from api.classes.game import *

from api.models.buildings import Buildings as buildings_db
from api.models.characters import Characters as characters_db
from api.models.game import Game as game_db
from api.models.players import Players as players_db
from api.models.removed_characters import RemovedCharacters as removed_characters_db

import api.responses as responses

from api.services import database

from api.utils import game_helpers, helpers, transactions


def end_turn(game_uuid, player_uuid):
    try:
        game = transactions.get_game(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        if game.state != ClassState.turn_phase.value:  # check if game is in turn phase
            return responses.not_turn_phase()

        player = transactions.get_player(player_uuid)  # get player from database

        if not player:  # check if player does not exist
            return responses.not_found("player")

        game.players.append(player)  # add player to game object

        characters = transactions.get_player_characters(player_uuid)  # get characters in player's hand

        if not characters:  # check if player has characters
            return responses.not_found("characters", True)

        character = helpers.get_filtered_item(characters, "name", game.character_turn)  # get character

        if not character:  # check if character is not in player's hand
            return responses.not_character()

        if not character.income_received:  # check if the character has received an income
            return responses.must_receive_income_to_end_turn()

        game.log += "{player_name} as the {character_name} ends their turn.\n".format(player_name=player.name, character_name=character.name)  # update log

        players = transactions.get_players(game_uuid)  # get players in game

        if not players:  # check if player does not exist
            return responses.not_found("players", True)

        buildings = transactions.get_player_buildings(player.uuid)  # get districts in player's city

        if buildings:  # check if player has districts in their city
            for building in buildings:  # go through each district
                if building.ability_used:  # check if player used the district's ability this turn
                    success_update_building = database.update_row_in_db(buildings_db, building.uuid, dict(ability_used=False))  # update the ability flag for building in database

                    if not success_update_building:  # check if failed to update database
                        return responses.error_updating_database("building")

        next_character = game_helpers.define_next_character_turn(players, game.character_turn)  # get the name of the next character

        if next_character.name:  # check if there is a next character
            for player in players:  # go through players
                characters = transactions.get_player_characters(player.uuid)  # get characters in player's hand

                if not characters:  # check if player has characters
                    return responses.not_found("characters", True)

                character_next = helpers.get_filtered_item(characters, "name", next_character.name)  # get next character from characters

                if character_next:  # check if player has the next character
                    ability_used = character_next.ability_used  # get ability used flag

                    if character_next.name == ClassCharacterName.king.value:  # check if the next character is the king
                        ability_used = True  # update flag

                        for _player in players:  # go through players
                            if _player.crown:  # check if player currently has the crown
                                success_update_player = database.update_row_in_db(players_db, _player.uuid, dict(crown=False))  # update crown flag for player in database | old crown needs to be reset so the new crown can be set

                                if not success_update_player:  # check if failed to update database
                                    return responses.error_updating_database("player")

                        success_update_player = database.update_row_in_db(players_db, player.uuid, dict(crown=True))  # update crown flag for player in database | set the new crown

                        if not success_update_player:  # check if failed to update database
                            return responses.error_updating_database("player")

                    if character_next.name == ClassCharacterName.bishop.value:  # check if the next character is the bishop
                        ability_used = True  # update flag

                        for _player in players:  # go through players
                            if _player.protected:  # check if player is currently protected from the warlord
                                success_update_player = database.update_row_in_db(players_db, _player.uuid, dict(protected=False))  # update protected flag for previous player in database

                                if not success_update_player:  # check if failed to update database
                                    return responses.error_updating_database("player")

                        success_update_player = database.update_row_in_db(players_db, player.uuid, dict(protected=True))  # update protected flag for player in database

                        if not success_update_player:  # check if failed to update database
                            return responses.error_updating_database("player")

                    if character_next.robbed:  # check if character is robbed
                        coins = player.coins  # get coins from the player with the robbed character

                        success_update_player = database.update_row_in_db(players_db, player.uuid, dict(coins=0))  # update amount of coins for player in database

                        if not success_update_player:  # check if failed to update database
                            return responses.error_updating_database("player")

                        for _player in players:  # go through players again
                            _characters = transactions.get_player_characters(_player.uuid)  # get characters in player's hand

                            if not _characters:  # check if player has characters
                                return responses.not_found("characters", True)

                            character_thief = helpers.get_filtered_item(_characters, "name", ClassCharacterName.thief.value)  # get thief from characters

                            if character_thief:  # check if player has the thief
                                _player.coins += coins  # add coins

                                success_update_player = database.update_row_in_db(players_db, _player.uuid, dict(coins=_player.coins))  # update amount of coins for player in database

                                if not success_update_player:  # check if failed to update database
                                    return responses.error_updating_database("player")

                    success_update_character = database.update_row_in_db(characters_db, character_next.uuid, dict(open=True, ability_used=ability_used))  # update open and ability used flags for character in database

                    if not success_update_character:  # check if failed to update database
                        return responses.error_updating_database("character")

                    game.log += "The {character_name} is up next.\n".format(character_name=character_next.name)  # update log

        elif not next_character.name:  # check if there is no next character
            game.state = ClassState.finished.value  # update game state assuming game has ended

            player_city_first_completed = helpers.get_filtered_item(players, "city_first_completed", True)  # get first player with a completed city

            log = "One or more players have completed their city, so the game is finished.\n"  # default log

            if not player_city_first_completed:  # check if there is no player yet with a completed city | the game ends at the end of the round when a player has a completed city
                game.round += 1  # increase counter
                game.state = ClassState.selection_phase.value  # update game state

                log = "The round has been played out, so next up is the character selection.\n"  # update log since game hasn't ended

                success_delete_removed_characters = database.delete_rows_from_db(removed_characters_db, game_uuid=game_uuid)  # delete character from removed characters in database

                if not success_delete_removed_characters:  # check if failed to delete in database
                    return responses.error_deleting_database("removed characters")

                for player in players:  # go through players
                    characters = transactions.get_player_characters(player.uuid)  # get characters in player's hand

                    if not characters:  # check if player has characters
                        return responses.not_found("characters", True)

                    character_king = helpers.get_filtered_item(characters, "name", ClassCharacterName.king.value)  # get king from characters

                    if character_king:  # check if player has the king | player becomes king at the of the round if the character was assassinated during the round
                        for _player in players:  # go through players
                            if _player.crown:  # check if player currently has the crown
                                success_update_player = database.update_row_in_db(players_db, _player.uuid, dict(crown=False))  # update crown flag for player in database | old crown needs to be reset so the new crown can be set

                                if not success_update_player:  # check if failed to update database
                                    return responses.error_updating_database("player")

                        success_update_player = database.update_row_in_db(players_db, player.uuid, dict(crown=True))  # update king flag for player in database | set the new king

                        if not success_update_player:  # check if failed to update database
                            return responses.error_updating_database("player")

                        if character_king.assassinated:  # check if the king was assassinated
                            log += "{player_name} was the assassinated king and receives the crown as the heir.\n".format(player_name=player.name)  # update log

                players = transactions.get_players(game_uuid)  # get players in game again since we just updated the database

                if not players:  # check if player does not exist
                    return responses.not_found("players", True)

                success_delete_characters = []
                success_update_players = []
                for player in players:  # go through players
                    success_delete_characters.append(database.delete_rows_from_db(characters_db, player_uuid=player.uuid))  # delete character from player characters in database
                    success_update_players.append(database.update_row_in_db(players_db, player.uuid, dict(protected=False, select_expected=player.crown)))  # reset certain player flags

                if False in success_delete_characters:  # check if failed to delete in database
                    return responses.error_deleting_database("character")

                if False in success_update_players:  # check if database failed to update
                    return responses.error_updating_database("player")

                game.deck_characters = transactions.get_game_deck_characters(game_uuid)  # get characters in game

                game.set_character_division()  # define how many characters per player and how many are open or closed on the field

                game.set_initial_possible_and_removed_characters()  # set possible and removed characters which happens at the start of each round

                success_write_possible_characters = []
                for character in game.possible_characters:  # go through each possible character
                    success_write_possible_characters.append(transactions.write_character_to_possible_characters(game_uuid, character))  # write character to database

                if False in success_write_possible_characters:  # check if failed to write to database
                    return responses.error_writing_database("possible characters")

                log += "{line} round {round} {line}\n".format(line="=" * 40, round=game.round)  # update game log

                amount = game.characters_open + game.characters_closed - 1  # define how many characters are removed at the beginning of the round

                if game.amount_players < 4:  # check if less than 4 players
                    amount = 1  # define how many characters are removed at the beginning of the round

                text = "{amount} characters have".format(amount=amount)  # update log

                if amount == 1:  # check if only one card
                    text = "{amount} character has".format(amount=amount)  # update log

                log += "{text} been removed for this round.\n".format(text=text)  # update log

                success_write_removed_characters = []
                for character in game.removed_characters:  # go through each removed character
                    success_write_removed_characters.append(transactions.write_character_to_removed_characters(game_uuid, character))  # write character to database

                if False in success_write_removed_characters:  # check if failed to write to database
                    return responses.error_writing_database("removed characters")

            game.log += log  # update log

        success_update_game = database.update_row_in_db(game_db, game_uuid, dict(state=game.state, character_turn=next_character.name, round=game.round, log=game.log))  # update database with the latest information about the game state

        if not success_update_game:  # check if database failed to update
            return responses.error_updating_database("game")

        return responses.no_content()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()
