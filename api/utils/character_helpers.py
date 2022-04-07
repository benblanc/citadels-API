from collections import Counter
from copy import deepcopy

from api.classes.card import *

from api.models.buildings import Buildings as buildings_db
from api.models.cards import Cards as cards_db
from api.models.characters import Characters as characters_db
from api.models.deck_discard_pile import DeckDiscardPile as deck_discard_pile_db
from api.models.deck_districts import DeckDistricts as deck_districts_db
from api.models.players import Players as players_db

import api.responses as responses

from api.services import database

from api.utils import game_helpers, helpers, transactions


def __trade_cards_with_other_player(player_uuid, other_player_uuid, player_name):
    other_player = transactions.get_player(other_player_uuid)  # get player from database

    if not other_player:  # check if player does not exist
        return responses.not_found("player")

    log = "{player_name} as the magician swaps cards with {other_player_name}.\n".format(player_name=player_name, other_player_name=other_player.name)  # update log

    cards = transactions.get_player_cards(player_uuid)  # get cards in player's hand

    other_player_cards = transactions.get_player_cards(other_player_uuid)  # get cards in other player's hand

    error = game_helpers.update_districts_in_database(from_table=cards_db, to_table=cards_db, cards=deepcopy(cards), uuid=other_player_uuid, player_table=True, from_table_name="cards in player's hand", to_table_name="cards in other player's hand")  # write cards from magician's hand to other player's hand

    if error:  # check if something went wrong when updating the database
        return error

    error = game_helpers.update_districts_in_database(from_table=cards_db, to_table=cards_db, cards=deepcopy(other_player_cards), uuid=player_uuid, player_table=True, from_table_name="cards in other player's hand", to_table_name="cards in player's hand")  # write cards from other player's hand to magician's hand

    if error:  # check if something went wrong when updating the database
        return error

    return log


def __discard_and_draw_from_deck_districts(game_uuid, player_uuid, player_name, name_districts):
    name_count = dict(Counter(name_districts))  # count occurences of each color

    amount = sum(list(map(lambda count: count, name_count.values())))  # get amount of cards which will be discarded

    cards = transactions.get_player_cards(player_uuid)  # get cards in player's hand

    if not cards:  # check if the player has no district cards in their hand
        return responses.no_cards_in_hand()

    text = "card"

    if len(name_districts) > 1:  # check if more than one cards
        text = "cards"

    log = "{player_name} as the magician discards {amount} {text} to draw the same amount from the deck of districts.\n".format(player_name=player_name, amount=len(name_districts), text=text)  # update log

    _cards = deepcopy(cards)  # take a deepcopy of cards| database will be updated in game_helpers.update_districts_in_database function so it will manipulate the values which we don't want

    cards_for_discard_pile = []
    for name, count in name_count.items():  # go through the cards the magician wants to discard
        card_to_discard = helpers.get_filtered_item(cards, "name", name)

        if not card_to_discard:  # check if district cannot be built
            return responses.not_found("district")

        if card_to_discard.amount < count:  # check if the magician does not have enough to discard
            return responses.not_enough_cards_to_discard(card_to_discard.card.name)

        card_to_discard.amount = count  # set the amount the magician wants to discard

        cards_for_discard_pile.append(card_to_discard)  # add card to list

    for card in _cards:  # go through deep copy of cards in hand
        for discard in cards_for_discard_pile:  # go through cards to discard
            if card.name == discard.name:  # find card to build
                for index in range(discard.amount):  # repeat for the amount
                    card.amount -= 1  # reduce amount of copies of card in hand by 1

                    if card.amount < 0:  # check if negative value
                        card.amount = 0  # set proper null value

    error = game_helpers.update_districts_in_database(from_table=cards_db, to_table=deck_discard_pile_db, cards=deepcopy(cards_for_discard_pile), uuid=game_uuid, from_deck_cards_by_amount=_cards, from_table_name="cards in player's hand", to_table_name="discard pile")  # write the cards for the discard pile to the deck_discard_pile table and update/remove the cards for the discard pile from the cards in player's hand table

    if error:  # check if something went wrong when updating the database
        return error

    drawn_cards = game_helpers.draw_cards_from_deck_districts(game_uuid, amount)  # draw the discarded amount of cards from the deck of districts

    if isinstance(drawn_cards, dict):  # check if error message
        return drawn_cards  # in this case it will contain the error message

    deck_districts = transactions.get_game_deck_districts(game_uuid)  # get deck of districts

    error = game_helpers.update_districts_in_database(from_table=deck_districts_db, to_table=cards_db, cards=deepcopy(drawn_cards), uuid=player_uuid, from_deck_cards_by_amount=deck_districts, player_table=True, to_table_name="cards in player's hand")  # write the drawn cards to the drawn_cards table and update/remove the drawn cards from the deck_districts table

    if error:  # check if something went wrong when updating the database
        return error

    return log


def use_assassin_ability(game_uuid, name_character, player_name):
    characters_in_game = transactions.get_game_deck_characters(game_uuid)  # get all characters in game

    character_in_game = helpers.get_filtered_item(characters_in_game, "name", name_character)  # get character

    if not character_in_game:  # check if there is a character with the given name
        return responses.not_found("character")

    log = "{player_name} as the assassin kills the {character_name}.\n".format(player_name=player_name, character_name=name_character)  # update log

    players = transactions.get_players(game_uuid)  # get players in game

    if not players:  # check if player does not exist
        return responses.not_found("players", True)

    for player in players:  # go through players
        characters = transactions.get_player_characters(player.uuid)  # get characters in player's hand

        if not characters:  # check if player has characters
            return responses.not_found("characters", True)

        character_to_assassinate = helpers.get_filtered_item(characters, "name", name_character)  # get character to assassinate

        if character_to_assassinate:  # check if there is a character with the given name
            success_update_character = database.update_row_in_db(characters_db, character_to_assassinate.uuid, dict(assassinated=True))  # update assassinated flag for character in database

            if not success_update_character:  # check if failed to update database
                return responses.error_updating_database("character")

    return log


def use_thief_ability(game_uuid, name_character, player_name):
    characters_in_game = transactions.get_game_deck_characters(game_uuid)  # get all characters in game

    character_in_game = helpers.get_filtered_item(characters_in_game, "name", name_character)  # get character

    if not character_in_game:  # check if there is a character with the given name
        return responses.not_found("character")

    log = "{player_name} as the thief robs the {character_name}.\n".format(player_name=player_name, character_name=name_character)  # update log

    players = transactions.get_players(game_uuid)  # get players in game

    if not players:  # check if player does not exist
        return responses.not_found("players", True)

    for player in players:  # go through players
        characters = transactions.get_player_characters(player.uuid)  # get characters in player's hand

        if not characters:  # check if player has characters
            return responses.not_found("characters", True)

        character_to_rob = helpers.get_filtered_item(characters, "name", name_character)  # get character to rob

        if character_to_rob:  # check if there is a character with the given name
            cannot_rob = [  # character which cannot be robbed
                ClassCharacterName.assassin.value,
                ClassCharacterName.thief.value
            ]

            if character_to_rob.name in cannot_rob or character_to_rob.assassinated:  # check if thief can actually rob the character
                return responses.cannot_rob()

            success_update_character = database.update_row_in_db(characters_db, character_to_rob.uuid, dict(robbed=True))  # update assassinated flag for character in database

            if not success_update_character:  # check if failed to update database
                return responses.error_updating_database("character")

    return log


def use_magician_ability(game_uuid, player_uuid, other_player_uuid, player_name, name_districts):
    if other_player_uuid:  # check if uuid of another player was provided | the magician wants to swap cards with another player
        return __trade_cards_with_other_player(player_uuid, other_player_uuid, player_name)  # use ability and update log

    elif name_districts:  # check if district names were provided | the magician wants to discard districts to draw new ones
        return __discard_and_draw_from_deck_districts(game_uuid, player_uuid, player_name, name_districts)  # use ability and update log

    return responses.bad_request("other_player_uuid or name_districts")  # the required input was not provided


def use_warlord_ability(game_uuid, player, other_player_uuid, name_districts):
    other_player = transactions.get_player(other_player_uuid)  # get player from database

    if not other_player:  # check if player does not exist
        return responses.not_found("player")

    if other_player.protected:  # check if targeted player is protected from the warlord
        return responses.player_protected()

    if not name_districts:  # check if district to destroy is missing
        return responses.bad_request("name_districts")

    buildings = transactions.get_player_buildings(other_player_uuid)  # get cards in player's city

    amount = 0
    for building in buildings:  # go through buidlings
        amount += building.amount  # add amount

    if amount == 8:  # check if completed city
        return responses.completed_city()

    reduced_cost = 1  # warlord needs to pay one less coin to destroy a district

    great_wall = helpers.get_filtered_item(buildings, "name", ClassDistrictName.great_wall.value)  # get great wall

    if great_wall:  # check if other player has the great wall in their city
        reduced_cost = 0  # warlord needs to pay the full price

    building_to_destroy = helpers.get_filtered_item(buildings, "name", name_districts[0])  # get district to destroy

    if not building_to_destroy:  # check if district cannot be destroyed
        return responses.not_found("district")

    if building_to_destroy.name == ClassDistrictName.keep.value:  # check if player wants to destroy the keep
        return responses.not_keep()

    log = "{player_name} as the warlord destroys the {district_name} in {other_player_name}'s city.\n".format(player_name=player.name, district_name=building_to_destroy.name, other_player_name=other_player.name)  # update log

    cards_complete_info = ClassCard().get_districts()  # get cards in game with complete information

    card_complete_info = helpers.get_filtered_item(cards_complete_info, "name", building_to_destroy.name)  # get full info on district | extra validation before getting index 0 is not necessary because game knows player has the card

    if player.gold < card_complete_info.gold - reduced_cost:  # check if player does not have enough gold to destroy the district
        return responses.not_enough_gold()

    player.gold -= card_complete_info.gold - reduced_cost  # decrease gold for player

    success_update_player = database.update_row_in_db(players_db, player.uuid, dict(gold=player.gold))  # update amount of gold for player in database

    if not success_update_player:  # check if failed to update database
        return responses.error_updating_database("player")

    error = game_helpers.update_districts_in_database(from_table=buildings_db, to_table=deck_discard_pile_db, cards=deepcopy([building_to_destroy]), uuid=game_uuid, from_table_name="buildings", to_table_name="discard pile")  # write the cards for the discard pile to the deck_discard_pile table and update/remove the cards for the discard pile from the buildings table

    if error:  # check if something went wrong when updating the database
        return error

    other_player.score = game_helpers.calculate_score(other_player.uuid, other_player.city_first_completed)  # calculate score

    success_update_player = database.update_row_in_db(players_db, other_player.uuid, dict(score=other_player.score))  # update score for player in database

    if not success_update_player:  # check if failed to update database
        return responses.error_updating_database("player")

    return log


def use_secondary_ability(player, character):
    buildings = transactions.get_player_buildings(player.uuid)  # get cards in player's city

    cards_complete_info = ClassCard().get_districts()  # get cards in game with complete information

    school_of_magic = False

    color_count = {}
    for building in buildings:  # go through buildings
        card_complete_info = helpers.get_filtered_item(cards_complete_info, "name", building.name)  # get full info on district | extra validation before getting index 0 is not necessary because game knows player has the card

        if card_complete_info.name == ClassDistrictName.school_of_magic.value:  # check if player has the school of magic in their city
            school_of_magic = True  # update flag

        if card_complete_info.color not in color_count.keys():  # check if color not yet in object
            color_count[card_complete_info.color] = 0  # add color to count object

        color_count[card_complete_info.color] += 1  # increase count

    gold = 0
    color = ""

    if character.name == ClassCharacterName.king.value:  # check if the character is the king
        color = ClassColor.yellow.value  # set color

    elif character.name == ClassCharacterName.bishop.value:  # check if the character is the bishop
        color = ClassColor.blue.value  # set color

    elif character.name == ClassCharacterName.merchant.value:  # check if the character is the merchant
        color = ClassColor.green.value  # set color

    elif character.name == ClassCharacterName.warlord.value:  # check if the character is the warlord
        color = ClassColor.red.value  # set color

    if color in color_count.keys():  # check if player has any districts with the color
        gold = color_count[color]  # player gains gold for each district with that color in their city

    if school_of_magic:  # check if player has the school of magic
        gold += 1  # increase gold

    log = "{player_name} as the {character_name} receives {amount} gold for each {color} district in their city.\n".format(player_name=player.name, character_name=character.name, amount=gold, color=color)  # update log

    player.gold += gold  # add gold

    success_update_player = database.update_row_in_db(players_db, player.uuid, dict(gold=player.gold))  # update amount of gold for player in database

    if not success_update_player:  # check if failed to update database
        return responses.error_updating_database("player")

    return log
