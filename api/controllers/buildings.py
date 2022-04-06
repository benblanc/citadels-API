import logging, traceback

from copy import deepcopy

from api.classes.card import *
from api.classes.game import *

from api.models.buildings import Buildings as buildings_db
from api.models.deck_discard_pile import DeckDiscardPile as deck_discard_pile_db
from api.models.deck_districts import DeckDistricts as deck_districts_db
from api.models.cards import Cards as cards_db
from api.models.players import Players as players_db

import api.responses as responses

from api.services import database

from api.utils import game_helpers, transactions

from api.validation import query


def get_buildings(game_uuid, player_uuid, sort_order, order_by, limit, offset):
    try:
        game = transactions.get_game(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        player = transactions.get_player(player_uuid)  # get player from database

        if not player:  # check if player does not exist
            return responses.not_found("player")

        invalid_query = query.validate_query(sort_order, order_by, limit, offset, ['name'])  # validate query parameters

        if invalid_query:  # check if invalid query
            return responses.conflict(invalid_query)

        buildings = transactions.get_all_from_query(buildings_db, sort_order, order_by, limit, offset, uuid=player_uuid, player_table=True)  # get all from database based on query

        return responses.success_get_buildings(buildings)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def use_ability(game_uuid, player_uuid, name, target_name):
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

        if not name:  # check if name was provided
            return responses.no_district_name()

        buildings = transactions.get_player_buildings(player_uuid)  # get districts in player's city

        if not buildings:  # check if player has buildings
            return responses.not_found("buildings", True)

        building = helpers.get_filtered_item(buildings, "name", name)  # get building

        if not building:  # check if building in player's city
            return responses.not_found("building")

        if building.ability_used:  # check if player has already used the buildings effect
            return responses.already_used_district_ability()

        if building.name == ClassDistrictName.smithy.value:  # check if player wants to use the effect of the smithy
            if player.coins < 3:  # check if player has enough coins
                return responses.not_enough_coins()

            deck_districts = transactions.get_game_deck_districts(game_uuid)  # get deck of districts in game

            districts = game.separate_cards_by_name(deck_districts)  # get separated cards

            random.shuffle(districts)  # shuffle district cards

            game.deck_districts = districts  # add districts to game object

            drawn_cards = []
            for index in range(2):  # do it twice
                if not len(game.deck_districts):  # check if the deck of districts has any cards left | we'll need to add the discard pile to the deck
                    cards = transactions.get_game_discard_pile  # get discard pile in game

                    error = game_helpers.update_districts_in_database(from_table=deck_discard_pile_db, to_table=deck_districts_db, cards=deepcopy(cards), uuid=game_uuid, from_table_name="discard pile")  # write the discard pile cards to the deck of districts table and update/remove the discard pile cards from the discard pile table

                    if error:  # check if something went wrong when updating the database
                        return error

                    deck_districts = transactions.get_game_deck_districts(game_uuid)  # get deck of districts in game which now has the cards from the discard pile

                    districts = game.separate_cards_by_name(deck_districts)  # get separated cards

                    random.shuffle(districts)  # shuffle district cards

                    game.deck_districts = districts  # add districts to game object

                drawn_cards.append(game.draw_card_deck_districts())  # draw a card from the deck of districts and add it to the list

            drawn_cards = game.aggregate_cards_by_name(drawn_cards)  # update the amount per card

            error = game_helpers.update_districts_in_database(from_table=deck_districts_db, to_table=cards_db, cards=deepcopy(drawn_cards), uuid=player_uuid, from_deck_cards_by_amount=game.deck_districts_by_amount, player_table=True, to_table_name="drawn cards")  # write the drawn cards to the player cards table and update/remove the drawn cards from the deck_districts table

            if error:  # check if something went wrong when updating the database
                return error

            player.coins -= 3  # reduce coins

            success_update_player = database.update_row_in_db(players_db, player_uuid, dict(coins=player.coins))  # update amount of coins for player in database

            if not success_update_player:  # check if failed to update database
                return responses.error_updating_database("player")

            success_update_building = database.update_row_in_db(buildings_db, building.uuid, dict(ability_used=True))  # update ability used flags for building in database

            if not success_update_building:  # check if failed to update database
                return responses.error_updating_database("building")

        elif building.name == ClassDistrictName.laboratory.value:  # check if player wants to use the effect of the laboratory
            if not target_name:  # check if target name was provided
                return responses.no_target_district_name()

            cards = transactions.get_player_cards(player_uuid)  # get cards in player's hand

            if not cards:  # check if player has cards
                return responses.not_found("cards", True)

            card = helpers.get_filtered_item(cards, "name", target_name)  # get target card in player's hand

            if not card:  # check if card in player's hand
                return responses.not_found("card")

            card.amount -= 1  # one copy of the card needs to be discarded | manipulates card amount in list of cards in player's hand

            _card = deepcopy(card)  # copy object so it doesn't manipulate list of cards in player's hand

            _card.amount = 1  # one copy of the card needs to be discarded

            error = game_helpers.update_districts_in_database(from_table=cards_db, to_table=deck_discard_pile_db, cards=deepcopy([_card]), uuid=game_uuid, from_deck_cards_by_amount=deepcopy(cards), to_table_name="discard pile")  # write the card in the player's hand to the discard pile table and update/remove the card from the player's hand table

            if error:  # check if something went wrong when updating the database
                return error

            player.coins += 1  # increase coins

            success_update_player = database.update_row_in_db(players_db, player_uuid, dict(coins=player.coins))  # update amount of coins for player in database

            if not success_update_player:  # check if failed to update database
                return responses.error_updating_database("player")

            success_update_building = database.update_row_in_db(buildings_db, building.uuid, dict(ability_used=True))  # update ability used flags for building in database

            if not success_update_building:  # check if failed to update database
                return responses.error_updating_database("building")

        return responses.no_content()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()
