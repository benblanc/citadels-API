import logging, traceback, random

from copy import deepcopy

from api.classes.card import *
from api.classes.game import *
from api.classes.player import *

from api.models.buildings import Buildings as buildings_db
from api.models.cards import Cards as cards_db
from api.models.characters import Characters as characters_db
from api.models.deck_discard_pile import DeckDiscardPile as deck_discard_pile_db
from api.models.deck_districts import DeckDistricts as deck_districts_db
from api.models.drawn_cards import DrawnCards as drawn_cards_db
from api.models.game import Game as game_db
from api.models.players import Players as players_db
from api.models.possible_characters import PossibleCharacters as possible_characters_db
from api.models.removed_characters import RemovedCharacters as removed_characters_db

import api.responses as responses

from api.services import database

from api.utils import helpers, transactions

from api.validation import query


def __define_next_character_turn(players, current_character_name):
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


def __update_districts_in_database(from_table, to_table, cards, uuid, from_deck_cards_by_amount=None, player_table=False, from_table_name="deck of districts", to_table_name="deck of districts"):  # write districts to new database table and update/delete from old database table
    updated_districts = []  # to avoid updating already updated districts (with the same value)
    deleted_districts = []  # to avoid deleting already deleted districts

    for card in cards:  # go through each card in object
        if player_table:  # check if the card needs to be written to a player related database table
            cards_in_table = to_table.query.filter_by(name=card.name, player_uuid=uuid).first()  # get cards

            if cards_in_table:  # check if the table already has a card with that name
                amount = cards_in_table.amount + card.amount  # increase amount
                card_uuid = cards_in_table.uuid  # get card uuid (before db session closes)

                success_update_card = database.update_row_in_db(to_table, card_uuid, dict(amount=amount))  # update card amount in to_table in database

                if not success_update_card:  # check if failed to update database
                    return responses.error_updating_database(to_table_name)

            else:  # table does not yet have a card with that name
                success_write_card = database.write_row_to_db(to_table(  # write card to database
                    uuid=helpers.create_uuid(),
                    name=card.name,
                    amount=card.amount,
                    player_uuid=uuid))

                if not success_write_card:  # check if failed to write to database
                    return responses.error_writing_database(to_table_name)

        else:  # card needs to be written to a game related database table
            cards_in_table = to_table.query.filter_by(name=card.name, game_uuid=uuid).first()  # get cards

            if cards_in_table:  # check if the table already has a card with that name
                amount = cards_in_table.amount + card.amount  # increase amount
                card_uuid = cards_in_table.uuid  # get card uuid (before db session closes)

                success_update_card = database.update_row_in_db(to_table, card_uuid, dict(amount=amount))  # update card amount in to_table in database

                if not success_update_card:  # check if failed to update database
                    return responses.error_updating_database(to_table_name)

            else:  # table does not yet have a card with that name
                success_write_card = database.write_row_to_db(to_table(  # write card to database
                    uuid=helpers.create_uuid(),
                    name=card.name,
                    amount=card.amount,
                    game_uuid=uuid))

                if not success_write_card:  # check if failed to write to database
                    return responses.error_writing_database(to_table_name)

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


def __calculate_score(player_uuid, city_first_completed):
    player_buildings_complete_info = []
    score = 0

    cards_complete_info = ClassCard().get_districts()  # get cards in game with complete information

    buildings = transactions.get_player_buildings(player_uuid)  # get cards in player's city

    for building in buildings:  # go through buildings in city
        card_complete_info = helpers.get_filtered_item(cards_complete_info, "name", building.name)  # get complete info on buildings

        for index in range(building.amount):  # go through amount
            player_buildings_complete_info.append(card_complete_info)  # add card to list

    all_colors = list(set(map(lambda building: building.color, player_buildings_complete_info)))  # get colors of buildings

    for building in player_buildings_complete_info:  # go through buildings with full info
        score += building.value  # add building value to score

    if len(all_colors) == 5:  # check if city has districts of all colors
        score += 3  # add bonus

    if len(player_buildings_complete_info) >= 8:  # check if city is completed
        score += 2  # add bonus

    if city_first_completed:  # check if player is the first to have a completed city
        score += 2  # add bonus

    return score


def get_players(game_uuid, sort_order, order_by, limit, offset):
    try:
        game = transactions.get_game(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        invalid_query = query.validate_query(sort_order, order_by, limit, offset, ['created', 'name'])  # validate query parameters

        if invalid_query:  # check if invalid query
            return responses.conflict(invalid_query)

        players = transactions.get_all_from_query(players_db, sort_order, order_by, limit, offset, uuid=game_uuid, default_order_by="created")  # get all from database based on query

        return responses.success_get_players(players)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def get_player(game_uuid, player_uuid):
    try:
        game = transactions.get_game(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        player = transactions.get_player(player_uuid)  # get player from database

        if player:  # check if player does not exist
            return responses.success_get_player(player)

        return responses.not_found()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


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

        if player.coins < card_complete_info.coins:  # check if the player does not have enough coins
            return responses.not_enough_coins()

        player.coins -= card_complete_info.coins  # decrease coin amount

        _cards = deepcopy(cards)  # take a deepcopy of cards| database will be updated in __update_districts_in_database function so it will manipulate the values which we don't want

        card_to_build.amount = 1  # build 1 district (not more)

        for card in _cards:  # go through deep copy of cards in hand
            if card.name == card_to_build.name:  # find card to build
                card.amount -= 1  # reduce amount of copies of card in hand by 1

                if card.amount < 0:  # check if negative value
                    card.amount = 0  # set proper null value

        error = __update_districts_in_database(from_table=cards_db, to_table=buildings_db, cards=[card_to_build], uuid=player_uuid, from_deck_cards_by_amount=_cards, player_table=True, from_table_name="cards in player's hand", to_table_name="buildings")  # write the district card to the buildings table and update/remove the district card from the cards table

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

        player.score = __calculate_score(player_uuid, player.city_first_completed)  # calculate score

        success_update_player = database.update_row_in_db(players_db, player.uuid, dict(coins=player.coins, city_first_completed=player.city_first_completed, score=player.score))  # update amount of coins, first to complete city flag and score for player in database

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

            deck_districts = transactions.get_game_deck_districts(game_uuid)  # get deck of districts in game

            districts = game.separate_cards_by_name(deck_districts)  # get separated cards

            random.shuffle(districts)  # shuffle district cards

            game.deck_districts = districts  # add districts to game object

            drawn_cards = []
            for index in range(2):  # do it twice
                if not len(game.deck_districts):  # check if the deck of districts has any cards left | we'll need to add the discard pile to the deck
                    cards = transactions.get_game_discard_pile  # get discard pile in game

                    error = __update_districts_in_database(from_table=deck_discard_pile_db, to_table=deck_districts_db, cards=cards, uuid=game_uuid, from_table_name="discard pile")  # write the discard pile cards to the deck of districts table and update/remove the discard pile cards from the discard pile table

                    if error:  # check if something went wrong when updating the database
                        return error

                    deck_districts = transactions.get_game_deck_districts(game_uuid)  # get deck of districts in game which now has the cards from the discard pile

                    districts = game.separate_cards_by_name(deck_districts)  # get separated cards

                    random.shuffle(districts)  # shuffle district cards

                    game.deck_districts = districts  # add districts to game object

                drawn_cards.append(game.draw_card_deck_districts())  # draw a card from the deck of districts and add it to the list

            drawn_cards = game.aggregate_cards_by_name(drawn_cards)  # update the amount per card

            error = __update_districts_in_database(from_table=deck_districts_db, to_table=cards_db, cards=drawn_cards, uuid=player_uuid, from_deck_cards_by_amount=game.deck_districts_by_amount, player_table=True, to_table_name="drawn cards")  # write the drawn cards to the drawn_cards table and update/remove the drawn cards from the deck_districts table

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

        deck_districts = transactions.get_game_deck_districts(game_uuid)  # get deck of districts in game

        districts = game.separate_cards_by_name(deck_districts)  # get separated cards

        random.shuffle(districts)  # shuffle district cards

        game.deck_districts = districts  # add districts to game object

        drawn_cards = []
        for index in range(2):  # do it twice
            if not len(game.deck_districts):  # check if the deck of districts has any cards left | we'll need to add the discard pile to the deck
                cards = transactions.get_game_discard_pile(game_uuid)  # get discard pile in game

                error = __update_districts_in_database(from_table=deck_discard_pile_db, to_table=deck_districts_db, cards=cards, uuid=game_uuid, from_table_name="discard pile")  # write the discard pile cards to the deck of districts table and update/remove the discard pile cards from the discard pile table

                if error:  # check if something went wrong when updating the database
                    return error

                deck_districts = transactions.get_game_deck_districts(game_uuid)  # get deck of districts in game which now has the cards from the discard pile

                districts = game.separate_cards_by_name(deck_districts)  # get separated cards

                random.shuffle(districts)  # shuffle district cards

                game.deck_districts = districts  # add districts to game object

            drawn_cards.append(game.draw_card_deck_districts())  # draw a card from the deck of districts and add it to the list

        drawn_cards = game.aggregate_cards_by_name(drawn_cards)  # update the amount per card

        error = __update_districts_in_database(from_table=deck_districts_db, to_table=drawn_cards_db, cards=drawn_cards, uuid=player_uuid, from_deck_cards_by_amount=game.deck_districts_by_amount, player_table=True, to_table_name="drawn cards")  # write the drawn cards to the drawn_cards table and update/remove the drawn cards from the deck_districts table

        if error:  # check if something went wrong when updating the database
            return error

        return responses.no_content()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def start_game(game_uuid, player_uuid):
    try:
        game = transactions.get_game(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        if game.state != ClassState.created.value:  # check if game has already started
            return responses.already_started()

        player = transactions.get_player(player_uuid)  # get player from database

        if not player:  # check if player does not exist
            return responses.not_found("player")

        if not player.hosting:  # check if the player is not hosting the game
            return responses.not_host()

        settings = transactions.get_game_settings(game_uuid)  # get settings from database

        if not settings:  # check if game settings do not exist
            return responses.not_found("settings", True)

        if game.amount_players < game.settings.min_players:  # check if there are not enough players
            return responses.not_enough_players()

        game.state = ClassState.started.value  # update game to say it has started

        success_update_game = database.update_row_in_db(game_db, game_uuid, dict(state=game.state))  # update database to say game has started

        if not success_update_game:  # check if database failed to update
            return responses.error_updating_database("game")

        deck_districts = transactions.get_game_deck_districts(game_uuid)  # get deck of districts in game

        districts = game.separate_cards_by_name(deck_districts)  # get separated cards

        random.shuffle(districts)  # shuffle district cards

        game.deck_districts = districts  # add districts to game object

        players = transactions.get_players(game_uuid)  # get players in game

        if not players:  # check if there are no players
            return responses.not_found("players", True)

        game.players = players  # add players to game object

        game.set_seat_per_player()  # define each player's position

        game.set_starting_coins_per_player()  # give each player coins to start with

        game.set_starting_hand_per_player()  # give each player district cards to start with

        game.set_starting_king()  # let a random player start as the king

        game.set_character_division()  # define how many characters per player and how many are open or closed on the field

        for player in game.players:  # go through each player
            success_update_player = database.update_row_in_db(players_db, player.uuid, dict(seat=player.seat, coins=player.coins, king=player.king, select_expected=player.select_expected))  # update seat, amount of coins, king and select expected flag for player in database

            if not success_update_player:  # check if failed to update database
                return responses.error_updating_database("player")

            cards = game.aggregate_cards_by_name(player.cards)  # update the amount per card

            error = __update_districts_in_database(from_table=deck_districts_db, to_table=cards_db, cards=cards, uuid=player.uuid, from_deck_cards_by_amount=game.deck_districts_by_amount, player_table=True, to_table_name="card")

            if error:  # check if something went wrong when updating the database
                return error

        game.state = ClassState.selection_phase.value  # update game to say it is ready to let players select characters

        game.log += "The host started the game.\nEach player will now pick their character(s) for this round.\n"  # update game log

        game.log += "{line} round {round} {line}\n".format(line="=" * 40, round=game.round)  # update game log

        amount = game.characters_open + game.characters_closed - 1  # define how many characters are removed at the beginning of the round

        if game.amount_players < 4:  # check if less than 4 players
            amount = 1  # define how many characters are removed at the beginning of the round

        text = "{amount} characters have".format(amount=amount)  # update log

        if amount == 1:  # check if only one card
            text = "{amount} character has".format(amount=amount)  # update log

        game.log += "{text} been removed for this round.\n".format(text=text)  # update log

        success_update_game = database.update_row_in_db(game_db, game_uuid, dict(state=game.state, log=game.log))  # update database with the latest information about the game state

        if not success_update_game:  # check if database failed to update
            return responses.error_updating_database("game")

        game.deck_characters = transactions.get_game_deck_characters(game_uuid)  # get characters in game

        game.set_initial_possible_and_removed_characters()  # set possible and removed characters which happens at the start of each round

        success_write_possible_characters = []
        for character in game.possible_characters:  # go through each possible character
            success_write_possible_characters.append(transactions.write_character_to_possible_characters(game_uuid, character))  # write character to database

        if False in success_write_possible_characters:  # check if failed to write to database
            return responses.error_writing_database("possible characters")

        success_write_removed_characters = []
        for character in game.removed_characters:  # go through each removed character
            success_write_removed_characters.append(transactions.write_character_to_removed_characters(game_uuid, character))  # write character to database

        if False in success_write_removed_characters:  # check if failed to write to database
            return responses.error_writing_database("removed characters")

        return responses.no_content()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


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


def keep_card(game_uuid, player_uuid, name):
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

        card_for_hand = helpers.get_filtered_item(drawn_cards, "name", name)  # get district for player's hand

        if not card_for_hand:  # check if district cannot be kept
            return responses.not_found("district")

        cards_for_discard_pile = helpers.get_filtered_items(drawn_cards, "name", name, False)  # filter cards where the name is different from the card for the player's hand

        if card_for_hand.amount > 1:  # check if drawn cards have multiple copies of the same card
            amount_for_discard_pile = card_for_hand.amount - 1  # keep 1 and the rest is for the discard pile

            cards_for_discard_pile.append(card_for_hand)  # add card(s) to discard pile
            cards_for_discard_pile[0].amount = amount_for_discard_pile  # set right amount

            card_for_hand.amount = 1  # set right amount

        error = __update_districts_in_database(from_table=drawn_cards_db, to_table=deck_discard_pile_db, cards=cards_for_discard_pile, uuid=game_uuid, from_table_name="drawn cards", to_table_name="discard pile")  # write the cards for the discard pile to the deck_discard_pile table and update/remove the cards for the discard pile from the drawn_cards table

        if error:  # check if something went wrong when updating the database
            return error

        error = __update_districts_in_database(from_table=drawn_cards_db, to_table=cards_db, cards=[card_for_hand], uuid=player_uuid, player_table=True, from_table_name="drawn cards", to_table_name="cards in the player's hand")  # write the cards for the player's hand to the cards table and update/remove the cards for the player's hand from the drawn_cards table

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

            deck_districts = transactions.get_game_deck_districts(game_uuid)  # get deck of districts in game

            districts = game.separate_cards_by_name(deck_districts)  # get separated cards

            random.shuffle(districts)  # shuffle district cards

            game.deck_districts = districts  # add districts to game object

            drawn_cards = []
            for index in range(2):  # do it twice
                if not len(game.deck_districts):  # check if the deck of districts has any cards left | we'll need to add the discard pile to the deck
                    cards = transactions.get_game_discard_pile(game_uuid)  # get discard pile in game

                    error = __update_districts_in_database(from_table=deck_discard_pile_db, to_table=deck_districts_db, cards=cards, uuid=game_uuid, from_table_name="discard pile")  # write the discard pile cards to the deck of districts table and update/remove the discard pile cards from the discard pile table

                    if error:  # check if something went wrong when updating the database
                        return error

                    deck_districts = transactions.get_game_deck_districts(game_uuid)  # get deck of districts in game which now has the cards from the discard pile

                    districts = game.separate_cards_by_name(deck_districts)  # get separated cards

                    random.shuffle(districts)  # shuffle district cards

                    game.deck_districts = districts  # add districts to game object

                drawn_cards.append(game.draw_card_deck_districts())  # draw a card from the deck of districts and add it to the list

            drawn_cards = game.aggregate_cards_by_name(drawn_cards)  # update the amount per card

            error = __update_districts_in_database(from_table=deck_districts_db, to_table=cards_db, cards=drawn_cards, uuid=player_uuid, from_deck_cards_by_amount=game.deck_districts_by_amount, player_table=True, to_table_name="drawn cards")  # write the drawn cards to the drawn_cards table and update/remove the drawn cards from the deck_districts table

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

        if main:  # check if character ability was the main ability
            if character.name == ClassCharacterName.assassin.value:  # check if the character is the assassin
                character_possible = False

                characters_in_game = transactions.get_game_deck_characters(game_uuid)  # get all characters in game

                if characters_in_game:  # check if there are characters in the game
                    character_in_game = helpers.get_filtered_item(characters_in_game, "name", name_character)  # get character

                    if character_in_game:  # check if there is a character with the given name
                        character_possible = True  # character is in game

                if not character_possible:  # check if character cannot be picked
                    return responses.not_found("character")

                log += "{player_name} as the assassin kills the {character_name}.\n".format(player_name=player.name, character_name=name_character)  # update log

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

            elif character.name == ClassCharacterName.thief.value:  # check if the character is the thief
                character_possible = False

                characters_in_game = transactions.get_game_deck_characters(game_uuid)  # get all characters in game

                if characters_in_game:  # check if there are characters in the game
                    character_in_game = helpers.get_filtered_item(characters_in_game, "name", name_character)  # get character

                    if character_in_game:  # check if there is a character with the given name
                        character_possible = True  # character is in game

                if not character_possible:  # check if character cannot be picked
                    return responses.not_found("character")

                log += "{player_name} as the thief robs the {character_name}.\n".format(player_name=player.name, character_name=name_character)  # update log

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
                            ClassCharacterName.assassin,
                            ClassCharacterName.thief
                        ]

                        if character_to_rob.name in cannot_rob or character_to_rob.assassinated:  # check if thief can actually rob the character
                            return responses.cannot_rob()

                        success_update_character = database.update_row_in_db(characters_db, character_to_rob.uuid, dict(robbed=True))  # update assassinated flag for character in database

                        if not success_update_character:  # check if failed to update database
                            return responses.error_updating_database("character")

            elif character.name == ClassCharacterName.magician.value:  # check if the character is the magician
                if other_player_uuid:  # check if uuid of another player was provided | the magician wants to swap cards with another player
                    other_player = transactions.get_player(other_player_uuid)  # get player from database

                    if not other_player:  # check if player does not exist
                        return responses.not_found("player")

                    log += "{player_name} as the magician swaps cards with {other_player_name}.\n".format(player_name=player.name, other_player_name=other_player.name)  # update log

                    cards = transactions.get_player_cards(player_uuid)  # get cards in player's hand

                    other_player_cards = transactions.get_player_cards(other_player_uuid)  # get cards in other player's hand

                    error = __update_districts_in_database(from_table=cards_db, to_table=cards_db, cards=cards, uuid=other_player_uuid, player_table=True, from_table_name="cards in player's hand", to_table_name="cards in other player's hand")  # write cards from magician's hand to other player's hand

                    if error:  # check if something went wrong when updating the database
                        return error

                    error = __update_districts_in_database(from_table=cards_db, to_table=cards_db, cards=other_player_cards, uuid=player_uuid, player_table=True, from_table_name="cards in other player's hand", to_table_name="cards in player's hand")  # write cards from other player's hand to magician's hand

                    if error:  # check if something went wrong when updating the database
                        return error

                elif name_districts:  # check if district names were provided | the magician wants to discard districts to draw new ones
                    name_count = {}
                    amount = 0

                    for name in name_districts:  # go through names
                        if name not in name_count.keys():  # check if name not yet in object
                            name_count[name] = 0  # add name to count object

                        name_count[name] += 1  # increase count
                        amount += 1  # increase amount

                    cards = transactions.get_player_cards(player_uuid)  # get cards in player's hand

                    if not cards:  # check if the player has no district cards in their hand
                        return responses.no_cards_in_hand()

                    text = "card"

                    if len(name_districts) > 1:  # check if more than one cards
                        text = "cards"

                    log += "{player_name} as the magician discards {amount} {text} to draw the same amount from the deck of districts.\n".format(player_name=player.name, amount=len(name_districts), text=text)  # update log

                    _cards = deepcopy(cards)  # take a deepcopy of cards| database will be updated in __update_districts_in_database function so it will manipulate the values which we don't want

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
                        for _card in cards_for_discard_pile:  # go through cards to discard
                            if card.name == _card.name:  # find card to build
                                card.amount -= 1  # reduce amount of copies of card in hand by 1

                                if card.amount < 0:  # check if negative value
                                    card.amount = 0  # set proper null value

                    error = __update_districts_in_database(from_table=cards_db, to_table=deck_discard_pile_db, cards=cards_for_discard_pile, uuid=game_uuid, from_deck_cards_by_amount=_cards, from_table_name="cards in player's hand", to_table_name="discard pile")  # write the cards for the discard pile to the deck_discard_pile table and update/remove the cards for the discard pile from the cards in player's hand table

                    if error:  # check if something went wrong when updating the database
                        return error

                    deck_districts = transactions.get_game_deck_districts(game_uuid)  # get deck of districts in game

                    districts = game.separate_cards_by_name(deck_districts)  # get separated cards

                    random.shuffle(districts)  # shuffle district cards

                    game.deck_districts = districts  # add districts to game object

                    drawn_cards = []
                    for index in range(amount):  # do it for the amount of discarded districts
                        if not len(game.deck_districts):  # check if the deck of districts has any cards left | we'll need to add the discard pile to the deck
                            cards = transactions.get_game_discard_pile(game_uuid)  # get discard pile in game

                            error = __update_districts_in_database(from_table=deck_discard_pile_db, to_table=deck_districts_db, cards=cards, uuid=game_uuid, from_table_name="discard pile")  # write the discard pile cards to the deck of districts table and update/remove the discard pile cards from the discard pile table

                            if error:  # check if something went wrong when updating the database
                                return error

                            deck_districts = transactions.get_game_deck_districts(game_uuid)  # get deck of districts in game which now has the cards from the discard pile

                            districts = game.separate_cards_by_name(deck_districts)  # get separated cards

                            random.shuffle(districts)  # shuffle district cards

                            game.deck_districts = districts  # add districts to game object

                        drawn_cards.append(game.draw_card_deck_districts())  # draw a card from the deck of districts and add it to the list

                    drawn_cards = game.aggregate_cards_by_name(drawn_cards)  # update the amount per card

                    error = __update_districts_in_database(from_table=deck_districts_db, to_table=cards_db, cards=drawn_cards, uuid=player_uuid, from_deck_cards_by_amount=game.deck_districts_by_amount, player_table=True, to_table_name="cards in player's hand")  # write the drawn cards to the drawn_cards table and update/remove the drawn cards from the deck_districts table

                    if error:  # check if something went wrong when updating the database
                        return error

                else:  # the required input was not provided
                    return responses.bad_request("other_player_uuid or name_districts")

            elif character.name == ClassCharacterName.warlord.value:  # check if the character is the warlord
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

                building_to_destroy = helpers.get_filtered_item(buildings, "card", name_districts[0])  # get district to destroy

                if not building_to_destroy:  # check if district cannot be destroyed
                    return responses.not_found("district")

                log += "{player_name} as the warlord destroys the {district_name} in {other_player_name}'s city.\n".format(player_name=player.name, district_name=building_to_destroy[0].card.name, other_player_name=other_player.name)  # update log

                cards_complete_info = ClassCard().get_districts()  # get cards in game with complete information

                card_complete_info = helpers.get_filtered_item(cards_complete_info, "name", building_to_destroy[0].card.name)  # get full info on district | extra validation before getting index 0 is not necessary because game knows player has the card

                if player.coins < card_complete_info.coins - 1:  # check if player does not have enough coins to destroy the district
                    return responses.not_enough_coins()

                player.coins -= card_complete_info.coins - 1  # decrease coins for player

                success_update_player = database.update_row_in_db(players_db, player.uuid, dict(coins=player.coins))  # update amount of coins for player in database

                if not success_update_player:  # check if failed to update database
                    return responses.error_updating_database("player")

                error = __update_districts_in_database(from_table=buildings_db, to_table=deck_discard_pile_db, cards=building_to_destroy, uuid=game_uuid, from_table_name="buildings", to_table_name="discard pile")  # write the cards for the discard pile to the deck_discard_pile table and update/remove the cards for the discard pile from the buildings table

                if error:  # check if something went wrong when updating the database
                    return error

                other_player.score = __calculate_score(other_player.uuid, other_player.city_first_completed)  # calculate score

                success_update_player = database.update_row_in_db(players_db, other_player.uuid, dict(score=other_player.score))  # update score for player in database

                if not success_update_player:  # check if failed to update database
                    return responses.error_updating_database("player")

            success_update_character = database.update_row_in_db(characters_db, character.uuid, dict(ability_used=True))  # update ability used flag for character in database

        else:  # not main ability
            buildings = transactions.get_player_buildings(player_uuid)  # get cards in player's city

            cards_complete_info = ClassCard().get_districts()  # get cards in game with complete information

            color_count = {}
            for building in buildings:  # go through buildings
                card_complete_info = helpers.get_filtered_item(cards_complete_info, "name", building.name)  # get full info on district | extra validation before getting index 0 is not necessary because game knows player has the card

                if card_complete_info.color not in color_count.keys():  # check if color not yet in object
                    color_count[card_complete_info.color] = 0  # add color to count object

                color_count[card_complete_info.color] += 1  # increase count

            coins = 0
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
                coins = color_count[color]  # player gains coins for each district with that color in their city

            log += "{player_name} as the {character_name} receives {amount} coins for each {color} district in their city.\n".format(player_name=player.name, character_name=character.name, amount=coins, color=color)  # update log

            player.coins += coins  # add coins

            success_update_player = database.update_row_in_db(players_db, player_uuid, dict(coins=player.coins))  # update amount of coins for player in database

            if not success_update_player:  # check if failed to update database
                return responses.error_updating_database("player")

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

        next_character = __define_next_character_turn(players, game.character_turn)  # get the name of the next character

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
                            if _player.king:  # check if player is the current king
                                success_update_player = database.update_row_in_db(players_db, _player.uuid, dict(king=False))  # update king flag for player in database | old king needs to be reset so the new king can be set

                                if not success_update_player:  # check if failed to update database
                                    return responses.error_updating_database("player")

                        success_update_player = database.update_row_in_db(players_db, player.uuid, dict(king=True))  # update king flag for player in database | set the new king

                        if not success_update_player:  # check if failed to update database
                            return responses.error_updating_database("player")

                    if character_next.name == ClassCharacterName.bishop.value:  # check if the next character is the bishop
                        ability_used = True  # update flag

                        for _player in players:  # go through players
                            if _player.protected:  # check if player is the current king
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
                            if _player.king:  # check if player is the current king
                                success_update_player = database.update_row_in_db(players_db, _player.uuid, dict(king=False))  # update king flag for player in database | old king needs to be reset so the new king can be set

                                if not success_update_player:  # check if failed to update database
                                    return responses.error_updating_database("player")

                        success_update_player = database.update_row_in_db(players_db, player.uuid, dict(king=True))  # update king flag for player in database | set the new king

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
                    success_update_players.append(database.update_row_in_db(players_db, player.uuid, dict(protected=False, select_expected=player.king)))  # reset certain player flags

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
