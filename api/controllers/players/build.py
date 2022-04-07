import logging, traceback

from copy import deepcopy

from api.classes.card import *
from api.classes.game import *

from api.models.buildings import Buildings as buildings_db
from api.models.cards import Cards as cards_db
from api.models.characters import Characters as characters_db
from api.models.game import Game as game_db
from api.models.players import Players as players_db

import api.responses as responses

from api.services import database

from api.utils import game_helpers, helpers, transactions


def build(game_uuid, player_uuid, name):
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

        if not character.income_received:  # check if the character has already received an income
            return responses.must_receive_income_to_build()

        characters_complete_info = ClassCard().get_characters()  # get characters in game with complete information

        character_complete_info = helpers.get_filtered_item(characters_complete_info, "name", character.name)  # get full info on charcter | extra validation before getting index 0 is not necessary because game knows player has the character

        if character.built >= character_complete_info.max_built:  # check if the player's character has not reached the building limit
            return responses.building_limit()

        cards = transactions.get_player_cards(player_uuid)  # get cards in player's hand

        if not cards:  # check if the player has no district cards in their hand
            return responses.no_cards_in_hand()

        card_to_build = helpers.get_filtered_item(cards, "name", name)  # get district for to build from player's hand

        if not card_to_build:  # check if district cannot be built
            return responses.not_found("district")

        cards_complete_info = ClassCard().get_districts()  # get cards in game with complete information

        card_complete_info = helpers.get_filtered_item(cards_complete_info, "name", card_to_build.name)  # get full info on district | extra validation before getting index 0 is not necessary because game knows player has the card

        buildings = transactions.get_player_buildings(player_uuid)  # get cards in player's city

        buildings_amount = 0
        for building in buildings:  # go through buildings
            buildings_amount += building.amount  # increase amount

        if buildings_amount == 8 and character_complete_info.name != ClassCharacterName.architect.value:  # check if player already has a completed city and character is not the architect
            return responses.already_completed_city()

        building_names = list(map(lambda building: building.name, buildings))  # get building names

        if card_complete_info.name in building_names:  # check if player already has the district in their city
            return responses.already_in_city()

        if player.gold < card_complete_info.gold:  # check if the player does not have enough gold
            return responses.not_enough_gold()

        player.gold -= card_complete_info.gold  # decrease gold amount

        _cards = deepcopy(cards)  # take a deepcopy of cards| database will be updated in game_helpers.update_districts_in_database function so it will manipulate the values which we don't want

        card_to_build.amount = 1  # build 1 district (not more)

        for card in _cards:  # go through deep copy of cards in hand
            if card.name == card_to_build.name:  # find card to build
                card.amount -= 1  # reduce amount of copies of card in hand by 1

                if card.amount < 0:  # check if negative value
                    card.amount = 0  # set proper null value

        error = game_helpers.update_districts_in_database(from_table=cards_db, to_table=buildings_db, cards=deepcopy([card_to_build]), uuid=player_uuid, from_deck_cards_by_amount=_cards, player_table=True, from_table_name="cards in player's hand", to_table_name="buildings")  # write the district card to the buildings table and update/remove the district card from the cards table

        if error:  # check if something went wrong when updating the database
            return error

        buildings = transactions.get_player_buildings(player_uuid)  # get cards in player's city

        log = "{player_name} as the {character_name} builds the {district_name}.\n".format(player_name=player.name, character_name=character.name, district_name=card_complete_info.name)  # update log

        buildings_amount = 0
        for building in buildings:  # go through buildings
            buildings_amount += building.amount  # increase amount

        if buildings_amount == 8:  # check if player has a completed city
            log += "{player_name} has a completed city.\n".format(player_name=player.name)  # update log

            players = transactions.get_players(game_uuid)  # get players in game

            if not players:  # check if there are no players
                return responses.not_found("players", True)

            player_city_first_completed = helpers.get_filtered_item(players, "city_first_completed", True)  # get first player with a completed city

            if not player_city_first_completed:  # check if there is no other player who has already completed their city first
                player.city_first_completed = True  # this player is the first to complete their city

        player.score = game_helpers.calculate_score(player_uuid, player.city_first_completed)  # calculate score

        success_update_player = database.update_row_in_db(players_db, player.uuid, dict(gold=player.gold, city_first_completed=player.city_first_completed, score=player.score))  # update amount of gold, first to complete city flag and score for player in database

        if not success_update_player:  # check if failed to update database
            return responses.error_updating_database("player")

        success_update_character = database.update_row_in_db(characters_db, character.uuid, dict(built=character.built + 1))  # update amount of districts built for character in database

        if not success_update_character:  # check if failed to update database
            return responses.error_updating_database("player")

        game.log += log  # update log

        success_update_game = database.update_row_in_db(game_db, game_uuid, dict(log=game.log))  # update game log in the database

        if not success_update_game:  # check if database failed to update
            return responses.error_updating_database("game")

        return responses.no_content()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()
