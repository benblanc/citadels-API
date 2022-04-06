import random

from collections import Counter
from copy import deepcopy

from api.classes.card import *
from api.classes.game import *

from api.models.deck_discard_pile import DeckDiscardPile as deck_discard_pile_db
from api.models.deck_districts import DeckDistricts as deck_districts_db

import api.responses as responses

from api.services import database

from api.utils import helpers, transactions


def define_next_character_turn(players, current_character_name):
    characters_complete_info = ClassCard().get_characters()  # get characters in game with complete information

    current_character = helpers.get_filtered_item(characters_complete_info, "name", current_character_name)  # get complete info on current character

    lowest_character = ClassCharacter(order=10, name=None)  # keep track of character with the lowest order | start from the highest order number and work the way down

    for player in players:  # go through each player
        characters = transactions.get_player_characters(player.uuid)  # get characters in player's hand

        for character in characters:  # go through player's characters
            character_complete_info = helpers.get_filtered_item(characters_complete_info, "name", character.name)  # get complete info on character

            if current_character.order < character_complete_info.order < lowest_character.order and not character.assassinated:  # check if the order of the player's character is between the current one and the lowest one AND the character is not assassinated
                lowest_character = character_complete_info  # update the lowest character

    return lowest_character


def __update_district_in_database(to_table, uuid, card, to_table_name, player_table=False):
    target_card_in_table = transactions.get_card_from_table(to_table, card.name, uuid, player_table)  # get card

    if target_card_in_table:  # check if the table already has a card with that name
        success_update_card = database.update_row_in_db(to_table, target_card_in_table.uuid, dict(amount=target_card_in_table.amount + card.amount))  # update card amount in to_table in database

        if not success_update_card:  # check if failed to update database
            return responses.error_updating_database(to_table_name)

    else:  # table does not yet have a card with that name
        success_write_card = transactions.write_card_to_table(to_table, uuid, card, player_table)  # write card to database

        if not success_write_card:  # check if failed to write to database
            return responses.error_writing_database(to_table_name)


def update_districts_in_database(from_table, to_table, cards, uuid, from_deck_cards_by_amount=None, player_table=False, from_table_name="deck of districts", to_table_name="deck of districts"):  # write districts to new database table and update/delete from old database table
    updated_districts = []  # to avoid updating already updated districts (with the same value)
    deleted_districts = []  # to avoid deleting already deleted districts

    for card in cards:  # go through each card in object
        error = __update_district_in_database(to_table, uuid, card, to_table_name, player_table)  # update the district in the database

        if error:  # check if there is an error
            return error

        amount = 0  # amount by default

        if from_deck_cards_by_amount:  # check if parameter is not none
            district_by_amount = helpers.get_filtered_item(from_deck_cards_by_amount, "name", card.name)  # get current district from deck

            if district_by_amount:  # check if there is a district
                amount = district_by_amount.amount  # get amount

        if amount and card.name not in updated_districts:  # check if district still in deck of districts and not yet updated in database
            updated_districts.append(card.name)  # add district name to already updated districts

            success_update_deck_districts = database.update_row_in_db(from_table, card.uuid, dict(amount=amount))  # update card amount in deck of districts in database

            if not success_update_deck_districts:  # check if failed to update database
                return responses.error_updating_database(from_table_name)

        elif not amount and card.name not in deleted_districts:  # district no longer in deck of districts and not yet deleted in database
            deleted_districts.append(card.name)  # add district name to already deleted districts

            success_delete_district = database.delete_row_from_db(from_table, card.uuid)  # delete district from deck of districts in database

            if not success_delete_district:  # check if failed to delete in database
                return responses.error_deleting_database(from_table_name)


def calculate_score(player_uuid, city_first_completed):
    player_buildings_complete_info = []
    score = 0

    haunted_quarter = False

    cards_complete_info = ClassCard().get_districts()  # get cards in game with complete information

    buildings = transactions.get_player_buildings(player_uuid)  # get cards in player's city

    for building in buildings:  # go through buildings in city
        card_complete_info = helpers.get_filtered_item(cards_complete_info, "name", building.name)  # get complete info on buildings

        if card_complete_info.name == ClassDistrictName.haunted_quarter.value:  # check if player has the haunted quarter in their city
            haunted_quarter = True  # update flag

        for index in range(building.amount):  # go through amount
            player_buildings_complete_info.append(card_complete_info)  # add card to list

    all_colors = list(set(map(lambda building: building.color, player_buildings_complete_info)))  # get colors of buildings

    if haunted_quarter and len(all_colors) == 4:  # check if player has the haunted quarter and is one color short in their city
        colors = list(map(lambda building: building.color, player_buildings_complete_info))  # get colors without removing duplicates

        colors_count = dict(Counter(colors))  # count occurences of each color

        if colors_count[ClassColor.purple.value] > 1:  # check if haunted quarter is not the only purple district
            possible_colors = [
                ClassColor.red.value,
                ClassColor.yellow.value,
                ClassColor.blue.value,
                ClassColor.green.value,
                ClassColor.purple.value,
            ]

            missing_color = ""

            for color in possible_colors:  # go through all possible colors
                if color not in colors_count.keys():  # check if it is the missing color
                    missing_color = color  # set missing color

            all_colors.append(missing_color)  # add missing color

    for building in player_buildings_complete_info:  # go through buildings with full info
        score += building.value  # add building value to score

    if len(all_colors) == 5:  # check if city has districts of all colors
        score += 3  # add bonus

    if len(player_buildings_complete_info) >= 8:  # check if city is completed
        score += 2  # add bonus

    if city_first_completed:  # check if player is the first to have a completed city
        score += 2  # add bonus

    return score


def get_shuffled_deck_districts(game_uuid):
    districts = []

    deck_districts = transactions.get_game_deck_districts(game_uuid)  # get deck of districts in game

    if deck_districts:  # check if not empty
        game = ClassGame()  # initialize new game object

        districts = game.separate_cards_by_name(deck_districts)  # get separated cards

        random.shuffle(districts)  # shuffle district cards

    return districts


def draw_cards_from_deck_districts(game_uuid, amount):
    game = ClassGame()  # initialize new game object

    game.deck_districts = get_shuffled_deck_districts(game_uuid)  # add districts to game object

    drawn_cards = []
    for index in range(amount):  # repeat for the required amount
        if not len(game.deck_districts):  # check if the deck of districts has any cards left | we'll need to add the discard pile to the deck
            cards = transactions.get_game_discard_pile(game_uuid)  # get discard pile in game

            error = update_districts_in_database(from_table=deck_discard_pile_db, to_table=deck_districts_db, cards=deepcopy(cards), uuid=game_uuid, from_table_name="discard pile")  # write the discard pile cards to the deck of districts table and update/remove the discard pile cards from the discard pile table

            if error:  # check if something went wrong when updating the database
                return error

            game.deck_districts = get_shuffled_deck_districts(game_uuid)  # add districts to game object

        drawn_cards.append(game.draw_card_deck_districts())  # draw a card from the deck of districts and add it to the list

    return game.aggregate_cards_by_name(drawn_cards)  # update the amount per card
