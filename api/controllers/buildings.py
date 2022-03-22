import logging, traceback

from copy import deepcopy

from api.classes.card import *

from api.models.buildings import Buildings as buildings_db

import api.responses as responses

from api.utils import transactions

from api.validation import query


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


def __update_districts_in_database(from_table, to_table, cards, uuid, from_deck_cards_by_amount=None, player_table=False, from_table_name="deck of districts", to_table_name="deck of districts"):  # write districts to new database table and update/delete from old database table
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

                    error = __update_districts_in_database(from_table=deck_discard_pile_db, to_table=deck_districts_db, cards=deepcopy(cards), uuid=game_uuid, from_table_name="discard pile")  # write the discard pile cards to the deck of districts table and update/remove the discard pile cards from the discard pile table

                    if error:  # check if something went wrong when updating the database
                        return error

                    deck_districts = transactions.get_game_deck_districts(game_uuid)  # get deck of districts in game which now has the cards from the discard pile

                    districts = game.separate_cards_by_name(deck_districts)  # get separated cards

                    random.shuffle(districts)  # shuffle district cards

                    game.deck_districts = districts  # add districts to game object

                drawn_cards.append(game.draw_card_deck_districts())  # draw a card from the deck of districts and add it to the list

            drawn_cards = game.aggregate_cards_by_name(drawn_cards)  # update the amount per card

            error = __update_districts_in_database(from_table=deck_districts_db, to_table=cards_db, cards=deepcopy(drawn_cards), uuid=player_uuid, from_deck_cards_by_amount=game.deck_districts_by_amount, player_table=True, to_table_name="drawn cards")  # write the drawn cards to the player cards table and update/remove the drawn cards from the deck_districts table

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
            pass

        return responses.no_content()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()
