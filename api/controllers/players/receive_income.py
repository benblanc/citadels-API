import logging, traceback

from collections import Counter
from copy import deepcopy

from api.classes.card import *
from api.classes.game import *

from api.models.cards import Cards as cards_db
from api.models.characters import Characters as characters_db
from api.models.deck_discard_pile import DeckDiscardPile as deck_discard_pile_db
from api.models.deck_districts import DeckDistricts as deck_districts_db
from api.models.drawn_cards import DrawnCards as drawn_cards_db
from api.models.game import Game as game_db
from api.models.players import Players as players_db

import api.responses as responses

from api.services import database

from api.utils import game_helpers, helpers, transactions


def receive_coins(game_uuid, player_uuid):
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

        if character.income_received:  # check if the character has already received an income
            return responses.already_income_received()

        game.players[0].coins += 2  # increase coin amount

        log = "{player_name} as the {character_name} chooses coins for their income.\n".format(player_name=player.name, character_name=character.name)  # update log

        if character.name == ClassCharacterName.merchant.value and not character.ability_used:  # check if character is the merchant
            character.ability_used = True
            game.players[0].coins += 1  # gain an additional coin
            log += "{player_name} as the {character_name} receives a coin in addition to the income.\n".format(player_name=player.name, character_name=character.name)  # update log

        elif character.name == ClassCharacterName.architect.value and not character.ability_used:  # check if character is the architect
            character.ability_used = True

            log += "{player_name} as the {character_name} receives two cards in addition to the income.\n".format(player_name=player.name, character_name=character.name)  # update log

            drawn_cards = game_helpers.draw_cards_from_deck_districts(game_uuid, 2)  # draw 2 cards from the deck of districts

            if isinstance(drawn_cards, dict):  # check if error message
                return drawn_cards  # in this case it will contain the error message

            game.deck_districts = transactions.get_game_deck_districts(game_uuid)  # add districts to game object

            error = game_helpers.update_districts_in_database(from_table=deck_districts_db, to_table=cards_db, cards=deepcopy(drawn_cards), uuid=player_uuid, from_deck_cards_by_amount=game.deck_districts, player_table=True, to_table_name="drawn cards")  # write the drawn cards to the drawn_cards table and update/remove the drawn cards from the deck_districts table

            if error:  # check if something went wrong when updating the database
                return error

        success_update_player = database.update_row_in_db(players_db, player_uuid, dict(coins=game.players[0].coins))  # update amount of coins for player in database

        if not success_update_player:  # check if failed to update database
            return responses.error_updating_database("player")

        success_update_character = database.update_row_in_db(characters_db, character.uuid, dict(income_received=True, ability_used=character.ability_used))  # update income and ability used flags for character in database

        if not success_update_character:  # check if failed to update database
            return responses.error_updating_database("character")

        game.log += log  # update log

        success_update_game = database.update_row_in_db(game_db, game_uuid, dict(log=game.log))  # update game log in the database

        if not success_update_game:  # check if database failed to update
            return responses.error_updating_database("game")

        return responses.no_content()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def draw_cards(game_uuid, player_uuid):
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

        if character.income_received:  # check if the character has already received an income
            return responses.already_income_received()

        drawn_cards = transactions.get_player_drawn_cards(player_uuid)  # get drawn district cards

        if drawn_cards:  # check if the player has already drawn cards and still needs to choose between them
            return responses.already_cards_drawn()

        draw_amount = 2  # define how many cards are drawn

        buildings = transactions.get_player_buildings(player_uuid)  # get buildings in player's city

        for district in buildings:  # go through districts in player's city
            if district.name == ClassDistrictName.observatory.value:  # check if player has the observatory in their city
                draw_amount += 1  # increase amount of cards the player can keep

        drawn_cards = game_helpers.draw_cards_from_deck_districts(game_uuid, draw_amount)  # draw 2 cards from the deck of districts

        if isinstance(drawn_cards, dict):  # check if error message
            return drawn_cards  # in this case it will contain the error message

        game.deck_districts = transactions.get_game_deck_districts(game_uuid)  # add districts to game object

        error = game_helpers.update_districts_in_database(from_table=deck_districts_db, to_table=drawn_cards_db, cards=deepcopy(drawn_cards), uuid=player_uuid, from_deck_cards_by_amount=game.deck_districts, player_table=True, to_table_name="drawn cards")  # write the drawn cards to the drawn_cards table and update/remove the drawn cards from the deck_districts table

        if error:  # check if something went wrong when updating the database
            return error

        return responses.no_content()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def keep_card(game_uuid, player_uuid, names):
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

        if character.income_received:  # check if the character has already received an income
            return responses.already_income_received()

        drawn_cards = transactions.get_player_drawn_cards(player_uuid)  # get drawn district cards

        if not drawn_cards:  # check if the player has not yet drawn cards | the player can't pick beteen cards that have not been drawn
            return responses.no_cards_drawn()

        keep_amount = 1  # define how many cards can be kept

        buildings = transactions.get_player_buildings(player_uuid)  # get buildings in player's city

        for district in buildings:  # go through districts in player's city
            if district.name == ClassDistrictName.library.value:  # check if player has the library in their city
                keep_amount += 1  # increase amount of cards the player can keep

        if len(names) != keep_amount:  # check if player wants to keep more cards than is allowed
            return responses.too_many_cards_to_keep()

        names_count = dict(Counter(names))  # count occurences of names

        for name in names:  # go through names
            card = helpers.get_filtered_item(drawn_cards, "name", name)  # get district for player's hand

            if not card:  # check if district cannot be kept
                return responses.not_found("district")

            if card.amount < names_count[name]:  # check if there are not enough cards with the name
                return responses.not_enough_drawn_cards(names_count[name], name)

        separated_drawn_cards = game.separate_cards_by_name(drawn_cards)  # separate the drawn cards

        cards_for_hand = []
        cards_for_discard_pile = []

        for card in separated_drawn_cards:  # go through separated drawn cards
            if card.name in names:  # check if it is a card the player wants to keep
                cards_for_hand.append(card)  # add to list
                names.remove(card.name)  # remove the name from the cards the player wants to keep

            else:  # player does not want to keep the card
                cards_for_discard_pile.append(card)  # add to list

        cards_for_hand = game.aggregate_cards_by_name(cards_for_hand)  # put separated cards back together

        error = game_helpers.update_districts_in_database(from_table=drawn_cards_db, to_table=cards_db, cards=deepcopy(cards_for_hand), uuid=player_uuid, player_table=True, from_table_name="drawn cards", to_table_name="cards in the player's hand")  # write the cards for the player's hand to the cards table and update/remove the cards for the player's hand from the drawn_cards table

        if error:  # check if something went wrong when updating the database
            return error

        if cards_for_discard_pile:  # check if not empty
            cards_for_discard_pile = game.aggregate_cards_by_name(cards_for_discard_pile)  # put separated cards back together

            error = game_helpers.update_districts_in_database(from_table=drawn_cards_db, to_table=deck_discard_pile_db, cards=deepcopy(cards_for_discard_pile), uuid=game_uuid, from_table_name="drawn cards", to_table_name="discard pile")  # write the cards for the discard pile to the deck_discard_pile table and update/remove the cards for the discard pile from the drawn_cards table

            if error:  # check if something went wrong when updating the database
                return error

        log = "{player_name} as the {character_name} chooses cards for their income.\n".format(player_name=game.players[0].name, character_name=character.name)  # update log

        if character.name == ClassCharacterName.merchant.value and not character.ability_used:  # check if character is the merchant
            character.ability_used = True
            game.players[0].coins += 1  # gain an additional coin
            log += "{player_name} as the {character_name} receives a coin in addition to the income.\n".format(player_name=game.players[0].name, character_name=character.name)  # update log

        elif character.name == ClassCharacterName.architect.value and not character.ability_used:  # check if character is the architect
            character.ability_used = True

            log += "{player_name} as the {character_name} receives two cards in addition to the income.\n".format(player_name=game.players[0].name, character_name=character.name)  # update log

            drawn_cards = game_helpers.draw_cards_from_deck_districts(game_uuid, 2)  # draw 2 cards from the deck of districts

            if isinstance(drawn_cards, dict):  # check if error message
                return drawn_cards  # in this case it will contain the error message

            game.deck_districts = transactions.get_game_deck_districts(game_uuid)  # add districts to game object

            error = game_helpers.update_districts_in_database(from_table=deck_districts_db, to_table=cards_db, cards=deepcopy(drawn_cards), uuid=player_uuid, from_deck_cards_by_amount=game.deck_districts, player_table=True, to_table_name="drawn cards")  # write the drawn cards to the drawn_cards table and update/remove the drawn cards from the deck_districts table

            if error:  # check if something went wrong when updating the database
                return error

        success_update_player = database.update_row_in_db(players_db, player_uuid, dict(coins=game.players[0].coins))  # update amount of coins for player in database

        if not success_update_player:  # check if failed to update database
            return responses.error_updating_database("player")

        success_update_character = database.update_row_in_db(characters_db, character.uuid, dict(income_received=True, ability_used=character.ability_used))  # update open income and ability used flags for character in database

        if not success_update_character:  # check if failed to update database
            return responses.error_updating_database("character")

        game.log += log  # update log

        success_update_game = database.update_row_in_db(game_db, game_uuid, dict(log=game.log))  # update game log in the database

        if not success_update_game:  # check if database failed to update
            return responses.error_updating_database("game")

        return responses.no_content()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()
