import logging, traceback

from api.classes.card import *
from api.classes.game import *

from api.models.characters import Characters as characters_db
from api.models.game import Game as game_db

import api.responses as responses

from api.services import database

from api.utils import character_helpers, helpers, transactions


def use_ability(game_uuid, player_uuid, main, name_character, name_districts, other_player_uuid):
    try:
        game = transactions.get_game(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        if game.state != ClassState.turn_phase.value:  # check if game is in turn phase
            return responses.not_turn_phase()

        player = transactions.get_player(player_uuid)  # get player from database

        if not player:  # check if player does not exist
            return responses.not_found("player")

        characters = transactions.get_player_characters(player_uuid)  # get characters in player's hand

        if not characters:  # check if player has characters
            return responses.not_found("characters", True)

        character = helpers.get_filtered_item(characters, "name", game.character_turn)  # get character

        if not character:  # check if character is not in player's hand
            return responses.not_character()

        characters_complete_info = ClassCard().get_characters()  # get characters in game with complete information

        character_complete_info = helpers.get_filtered_item(characters_complete_info, "name", character.name)  # get full info on current character

        ability = helpers.get_filtered_item(character_complete_info.effect, "main", main)  # get character with effect

        if not ability:  # check if character does not have the ability
            return responses.not_found("ability")

        if main and character.ability_used:  # check if the player has already used the character's main ability
            return responses.already_used_ability()

        if not main and character.ability_additional_income_used:  # check if the player has already used the character's second ability
            return responses.already_used_ability(main=False)

        log = ""

        print(game_uuid, player_uuid, main, name_character, name_districts, other_player_uuid)
        print("game_uuid: ", game_uuid)
        print("player_uuid: ", player_uuid)
        print("main: ", main)
        print("name_character: ", name_character)
        print("name_districts: ", name_districts)
        print("other_player_uuid: ", other_player_uuid)

        if main:  # check if character ability was the main ability
            if character.name == ClassCharacterName.assassin.value:  # check if the character is the assassin
                log = character_helpers.use_assassin_ability(log, game_uuid, name_character, player.name)  # use assassin's ability and update log

                if isinstance(log, tuple):  # check if error message
                    return log  # in this case it will contain the error message

            elif character.name == ClassCharacterName.thief.value:  # check if the character is the thief
                log = character_helpers.use_thief_ability(log, game_uuid, name_character, player.name)  # use thief's ability and update log

                if isinstance(log, tuple):  # check if error message
                    return log  # in this case it will contain the error message

            elif character.name == ClassCharacterName.magician.value:  # check if the character is the magician
                log = character_helpers.use_magician_ability(log, game_uuid, player_uuid, other_player_uuid, player.name, name_districts)  # use magician's ability and update log

                if isinstance(log, tuple):  # check if error message
                    return log  # in this case it will contain the error message

            elif character.name == ClassCharacterName.warlord.value:  # check if the character is the warlord
                log = character_helpers.use_warlord_ability(log, game_uuid, player, other_player_uuid, name_districts)  # use warlord's ability and update log

                if isinstance(log, tuple):  # check if error message
                    return log  # in this case it will contain the error message

            success_update_character = database.update_row_in_db(characters_db, character.uuid, dict(ability_used=True))  # update ability used flag for character in database

        else:  # not main ability
            log = character_helpers.use_secondary_ability(log, player, character)  # use secondary ability and update log

            if isinstance(log, tuple):  # check if error message
                return log  # in this case it will contain the error message

            success_update_character = database.update_row_in_db(characters_db, character.uuid, dict(ability_additional_income_used=True))  # update ability for additional income used flags for character in database

        if not success_update_character:  # check if failed to update database
            return responses.error_updating_database("character")

        game.log += log  # update log

        success_update_game = database.update_row_in_db(game_db, game_uuid, dict(log=game.log))  # update database with the latest information about the game

        if not success_update_game:  # check if database failed to update
            return responses.error_updating_database("game")

        return responses.no_content()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()
