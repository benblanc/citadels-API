import logging, traceback, random

from api.classes.card import *
from api.classes.game import *
from api.classes.player import *

from api.models.characters import Characters as characters_db
from api.models.game import Game as game_db
from api.models.settings import Settings as settings_db
from api.models.deck_districts import DeckDistricts as deck_districts_db
from api.models.players import Players as players_db
from api.models.cards import Cards as cards_db
from api.models.deck_characters import DeckCharacters as deck_characters_db
from api.models.possible_characters import PossibleCharacters as possible_characters_db
from api.models.removed_characters import RemovedCharacters as removed_characters_db
from api.models.drawn_cards import DrawnCards as drawn_cards_db
from api.models.deck_discard_pile import DeckDiscardPile as deck_discard_pile_db

import api.responses as responses

from api.services import database

from api.utils import helpers

from api.validation import query

from pprint import pprint


def __update_districts_in_database(from_table, to_table, from_deck_cards_by_amount, cards, uuid, player_table=False):  # write districts to new database table and update/delete from old database table
    updated_districts = []  # to avoid updating already updated districts (with the same value)
    deleted_districts = []  # to avoid deleting already deleted districts

    for deck_district in cards:  # go through each card in object
        if player_table:  # check if the card needs to be written to a player related database table
            success_write_card = database.write_row_to_db(to_table(  # write card to database
                uuid=helpers.create_uuid(),
                name=deck_district.card.name,
                amount=deck_district.amount,
                player_uuid=uuid
            ))

        else:  # card needs to be written to a game related database table
            success_write_card = database.write_row_to_db(to_table(  # write card to database
                uuid=helpers.create_uuid(),
                name=deck_district.card.name,
                amount=deck_district.amount,
                game_uuid=uuid
            ))

        if not success_write_card:  # check if failed to write to database
            return responses.error_writing_database("card")

        amount = 0  # amount by default

        district_by_amount = list(filter(lambda item: item.card.name.lower() == deck_district.card.name.lower(), from_deck_cards_by_amount))  # get current district from deck

        if district_by_amount:  # check if there is a district
            amount = district_by_amount[0].amount  # get amount

        if amount and deck_district.card.name not in updated_districts:  # check if district still in deck of districts and not yet updated in database
            updated_districts.append(deck_district.card.name)  # add district name to already updated districts

            success_update_deck_districts = database.update_row_in_db(from_table, deck_district.card.uuid, dict(amount=amount))  # update card amount in deck of districts in database

            if not success_update_deck_districts:  # check if failed to update database
                return responses.error_updating_database("deck of districts")

        elif not amount and deck_district.card.name not in deleted_districts:  # district no longer in deck of districts and not yet deleted in database
            deleted_districts.append(deck_district.card.name)  # add district name to already deleted districts

            success_delete_district = database.delete_row_from_db(from_table, deck_district.card.uuid)  # delete district from deck of districts in database

            if not success_delete_district:  # check if failed to delete in database
                return responses.error_deleting_database("district")


def get_players(game_uuid, sort_order, order_by, limit, offset):
    try:
        game = game_db.query.get(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        default_sort_order = 'asc'
        default_order_by = 'created'
        default_limit = 0
        default_offset = 0

        invalid_query = query.validate_query(sort_order, order_by, limit, offset, ['created', 'name'])

        if invalid_query:
            return responses.conflict(invalid_query)

        if sort_order:  # check if not none
            default_sort_order = sort_order

        if order_by:  # check if not none
            default_order_by = order_by

        if limit:  # check if not none
            default_limit = limit

        if offset:  # check if not none
            default_offset = offset

        if default_order_by == 'created':
            sort = players_db.created
        elif default_order_by == 'name':
            sort = players_db.name

        if default_sort_order == 'asc':
            sort = sort.asc()
        elif default_sort_order == 'desc':
            sort = sort.desc()

        if default_limit == 0:
            players = players_db.query.filter_by(game_uuid=game_uuid).order_by(sort).offset(default_offset).all()
        else:
            players = players_db.query.filter_by(game_uuid=game_uuid).order_by(sort).limit(default_limit).offset(default_offset).all()

        return responses.success_get_players(players)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def get_player(game_uuid, player_uuid):
    try:
        game = game_db.query.get(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        player = players_db.query.get(player_uuid)

        if player:
            return responses.success_get_player(player)

        return responses.not_found()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def receive_coins(game_uuid, player_uuid):
    try:
        game = game_db.query.get(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        game = ClassGame(database_object=game)  # initialize game object

        if game.state != ClassState.turn_phase.value:  # check if game is in turn phase
            return responses.not_turn_phase()

        player = players_db.query.get(player_uuid)  # get player from database

        if not player:  # check if player does not exist
            return responses.not_found("player")

        game.players.append(ClassPlayer(database_object=player))  # add player to game object

        characters = characters_db.query.filter_by(player_uuid=player_uuid).all()  # get characters in player's hand

        if not characters:  # check if player has characters
            return responses.not_found("characters", True)

        character_in_hand = False

        characters = list(map(lambda character: ClassCharacter(database_object=character), characters))  # convert database objects to class objects

        character = list(filter(lambda character: character.name == game.character_turn, characters))  # get character

        if character:  # check if there is a character with the given name
            character = character[0]  # get character from list
            character_in_hand = True  # character is in player's hand

        if not character_in_hand:  # check if character is not in player's hand
            return responses.not_character()

        if character.income_received:  # check if the character has already received an income
            return responses.already_income_received()

        game.players[0].coins += 2  # increase coin amount

        success_update_player = database.update_row_in_db(players_db, player.uuid, dict(coins=game.players[0].coins))  # update amount of coins for player in database

        if not success_update_player:  # check if failed to update database
            return responses.error_updating_database("player")

        success_update_character = database.update_row_in_db(characters_db, character.uuid, dict(open=True, income_received=True))  # update open and income flags for character in database

        if not success_update_character:  # check if failed to update database
            return responses.error_updating_database("character")

        return responses.no_content()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def draw_cards(game_uuid, player_uuid):
    try:
        game = game_db.query.get(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        game = ClassGame(database_object=game)  # initialize game object

        if game.state != ClassState.turn_phase.value:  # check if game is in turn phase
            return responses.not_turn_phase()

        player = players_db.query.get(player_uuid)  # get player from database

        if not player:  # check if player does not exist
            return responses.not_found("player")

        game.players.append(ClassPlayer(database_object=player))  # add player to game object

        characters = characters_db.query.filter_by(player_uuid=player_uuid).all()  # get characters in player's hand

        if not characters:  # check if player has characters
            return responses.not_found("characters", True)

        character_in_hand = False

        characters = list(map(lambda character: ClassCharacter(database_object=character), characters))  # convert database objects to class objects

        character = list(filter(lambda character: character.name == game.character_turn, characters))  # get character

        if character:  # check if there is a character with the given name
            character = character[0]  # get character from list
            character_in_hand = True  # character is in player's hand

        if not character_in_hand:  # check if character is not in player's hand
            return responses.not_character()

        if character.income_received:  # check if the character has already received an income
            return responses.already_income_received()

        drawn_cards = drawn_cards_db.query.filter_by(player_uuid=player_uuid).all()  # get drawn district cards

        if drawn_cards:  # check if the player has already drawn cards and still needs to choose between them
            return responses.already_cards_drawn()

        deck_districts = deck_districts_db.query.filter_by(game_uuid=game_uuid).all()  # get deck of districts in game

        districts = []
        for district in deck_districts:  # go through each district in the deck of districts
            for index in range(district.amount):  # add the separated district to a new list as class objects
                districts.append(ClassDistrict(uuid=district.uuid, name=district.name))

        random.shuffle(districts)  # shuffle district cards

        game.deck_districts = districts  # add districts to game object

        # updated_districts = []  # to avoid updating already updated districts (with the same value)
        # deleted_districts = []  # to avoid deleting already deleted districts

        # cards = {}
        # for index in range(2):  # do it twice
        #     drawn_card = game.draw_card_deck_districts()  # draw a card from the deck of districts
        #
        #     if drawn_card.name not in cards.keys():  # check if card is not on new object
        #         cards[drawn_card.name] = ClassDeckDistrict(1, drawn_card)  # add card by amount to object
        #     else:  # card is in object
        #         new_deck_district = cards[drawn_card.name]  # get card from object
        #         new_deck_district.amount += 1  # increase amount
        #         cards[drawn_card.name] = new_deck_district  # update card in object

        drawn_cards = []
        for index in range(2):  # do it twice
            drawn_cards.append(game.draw_card_deck_districts())  # draw a card from the deck of districts and add it to the list

        drawn_cards = game.aggregate_cards_by_name(drawn_cards)  # update the amount per card

        __update_districts_in_database(deck_districts_db, drawn_cards_db, game.deck_districts_by_amount, drawn_cards, player_uuid, player_table=True)  # write the drawn cards to the drawn_cards table and update/remove the drawn cards from the deck_districts table

        # for _, deck_district in cards.items():  # go through each card in object
        #     success_write_card = database.write_row_to_db(drawn_cards_db(  # write card to database
        #         uuid=helpers.create_uuid(),
        #         name=deck_district.card.name,
        #         amount=deck_district.amount,
        #         player_uuid=player_uuid
        #     ))
        #
        #     if not success_write_card:  # check if failed to write to database
        #         return responses.error_writing_database("card")
        #
        #     amount = 0  # amount by default
        #
        #     district_by_amount = list(filter(lambda item: item.card.name.lower() == deck_district.card.name.lower(), game.deck_districts_by_amount))  # get current district from deck
        #
        #     if district_by_amount:  # check if there is a district
        #         amount = district_by_amount[0].amount  # get amount
        #
        #     if amount and deck_district.card.name not in updated_districts:  # check if district still in deck of districts and not yet updated in database
        #         updated_districts.append(deck_district.card.name)  # add district name to already updated districts
        #
        #         success_update_deck_districts = database.update_row_in_db(deck_districts_db, deck_district.card.uuid, dict(amount=amount))  # update card amount in deck of districts in database
        #
        #         if not success_update_deck_districts:  # check if failed to update database
        #             return responses.error_updating_database("deck of districts")
        #
        #     elif not amount and deck_district.card.name not in deleted_districts:  # district no longer in deck of districts and not yet deleted in database
        #         deleted_districts.append(deck_district.card.name)  # add district name to already deleted districts
        #
        #         success_delete_district = database.delete_row_from_db(deck_districts_db, deck_district.card.uuid)  # delete district from deck of districts in database
        #
        #         if not success_delete_district:  # check if failed to delete in database
        #             return responses.error_deleting_database("district")

        return responses.no_content()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def start_game(game_uuid, player_uuid):
    try:
        game = game_db.query.get(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        game = ClassGame(database_object=game)  # initialize game object

        if game.state != ClassState.created.value:  # check if game has already started
            return responses.already_started()

        player = players_db.query.get(player_uuid)  # get player from database

        if not player:  # check if player does not exist
            return responses.not_found("player")

        if not player.hosting:  # check if the player is not hosting the game
            return responses.not_host()

        settings = settings_db.query.filter_by(game_uuid=game_uuid).first()  # get settings from database

        if not settings:  # check if game settings do not exist
            return responses.not_found("settings", True)

        game.settings = ClassSettings(database_object=settings)  # add settings to game object

        if game.amount_players < game.settings.min_players:  # check if there are not enough players
            return responses.not_enough_players()

        game.state = ClassState.started.value  # update game to say it has started

        success_update_game = database.update_row_in_db(game_db, game_uuid, dict(state=game.state))  # update database to say game has started

        if not success_update_game:  # check if database failed to update
            return responses.error_updating_database("game")

        deck_districts = deck_districts_db.query.filter_by(game_uuid=game_uuid).all()  # get deck of districts in game

        districts = []
        for district in deck_districts:  # go through each district in the deck of districts
            for index in range(district.amount):  # add the separated district to a new list as class objects
                districts.append(ClassDistrict(uuid=district.uuid, name=district.name))

        random.shuffle(districts)  # shuffle district cards

        game.deck_districts = districts  # add districts to game object

        players = players_db.query.filter_by(game_uuid=game_uuid).all()  # get players in game

        if not players:  # check if there are no players
            return responses.not_found("players", True)

        game.players = list(map(lambda player: ClassPlayer(database_object=player), players))  # add players to game object

        game.set_seat_per_player()  # define each player's position

        game.set_starting_coins_per_player()  # give each player coins to start with

        game.set_starting_hand_per_player()  # give each player district cards to start with

        game.set_starting_king()  # let a random player start as the king

        game.set_character_division()  # define how many characters per player and how many are open or closed on the field

        updated_districts = []  # to avoid updating already updated districts (with the same value)
        deleted_districts = []  # to avoid deleting already deleted districts

        for player in game.players:  # go through each player
            success_update_player = database.update_row_in_db(players_db, player.uuid, dict(seat=player.seat, coins=player.coins, king=player.king, select_expected=player.select_expected))  # update seat, amount of coins, king and select expected flag for player in database

            if not success_update_player:  # check if failed to update database
                return responses.error_updating_database("player")

            cards = {}
            for card in player.cards:  # go through each card in the player's hand
                if card.name not in cards.keys():  # check if card is not on new object
                    cards[card.name] = ClassDeckDistrict(1, card)  # add card by amount to object
                else:  # card is in object
                    new_deck_district = cards[card.name]  # get card from object
                    new_deck_district.amount += 1  # increase amount
                    cards[card.name] = new_deck_district  # update card in object

            for _, deck_district in cards.items():  # go through each card in object
                success_write_card = database.write_row_to_db(cards_db(  # write card to database
                    uuid=helpers.create_uuid(),
                    name=deck_district.card.name,
                    amount=deck_district.amount,
                    player_uuid=player.uuid
                ))

                if not success_write_card:  # check if failed to write to database
                    return responses.error_writing_database("card")

                amount = 0  # amount by default

                district_by_amount = list(filter(lambda item: item.card.name.lower() == deck_district.card.name.lower(), game.deck_districts_by_amount))  # get current district from deck

                if district_by_amount:  # check if there is a district
                    amount = district_by_amount[0].amount  # get amount

                if amount and deck_district.card.name not in updated_districts:  # check if district still in deck of districts and not yet updated in database
                    updated_districts.append(deck_district.card.name)  # add district name to already updated districts

                    success_update_deck_districts = database.update_row_in_db(deck_districts_db, deck_district.card.uuid, dict(amount=amount))  # update card amount in deck of districts in database

                    if not success_update_deck_districts:  # check if failed to update database
                        return responses.error_updating_database("deck of districts")

                elif not amount and deck_district.card.name not in deleted_districts:  # district no longer in deck of districts and not yet deleted in database
                    deleted_districts.append(deck_district.card.name)  # add district name to already deleted districts

                    success_delete_district = database.delete_row_from_db(deck_districts_db, deck_district.card.uuid)  # delete district from deck of districts in database

                    if not success_delete_district:  # check if failed to delete in database
                        return responses.error_deleting_database("district")

        game.state = ClassState.selection_phase.value  # update game to say it is ready to let players select characters

        success_update_game = database.update_row_in_db(game_db, game_uuid, dict(state=game.state, characters_open=game.characters_open, characters_closed=game.characters_closed, characters_per_player=game.characters_per_player))  # update database with the latest information about the game state

        if not success_update_game:  # check if database failed to update
            return responses.error_updating_database("game")

        deck_characters = deck_characters_db.query.filter_by(game_uuid=game_uuid).all()  # get characters in game

        game.deck_characters = list(map(lambda character: ClassCharacter(database_object=character), deck_characters))  # add deck of characters to game object

        game.set_initial_possible_and_removed_characters()  # set possible and removed characters which happens at the start of each round

        success_write_possible_characters = []
        for character in game.possible_characters:  # go through each possible character
            success_write_possible_characters.append(database.write_row_to_db(possible_characters_db(  # write character to database
                uuid=helpers.create_uuid(),
                name=character.name,
                open=character.open,
                assassinated=character.assassinated,
                robbed=character.robbed,
                built=character.built,
                income_received=character.income_received,
                game_uuid=game_uuid)))

        if False in success_write_possible_characters:  # check if failed to write to database
            return responses.error_writing_database("possible characters")

        success_write_removed_characters = []
        for character in game.removed_characters:  # go through each removed character
            success_write_removed_characters.append(database.write_row_to_db(removed_characters_db(  # write character to database
                uuid=helpers.create_uuid(),
                name=character.name,
                open=character.open,
                assassinated=character.assassinated,
                robbed=character.robbed,
                built=character.built,
                income_received=character.income_received,
                game_uuid=game_uuid)))

        if False in success_write_removed_characters:  # check if failed to write to database
            return responses.error_writing_database("removed characters")

        return responses.no_content()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def select_character(game_uuid, player_uuid, name, remove):
    try:
        game = game_db.query.get(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        game = ClassGame(database_object=game)  # initialize game object

        if game.state != ClassState.selection_phase.value:  # check if game is in selection phase
            return responses.not_selection_phase()

        player = players_db.query.get(player_uuid)  # get player from database

        if not player:  # check if player does not exist
            return responses.not_found("player")

        if not player.select_expected:  # check if player needs to select character
            return responses.not_select_expected()

        game.players.append(ClassPlayer(database_object=player))  # add player to game object

        character_possible = False

        possible_characters = possible_characters_db.query.filter_by(game_uuid=game_uuid).all()  # get possible characters in game

        if possible_characters:  # check if there are possible characters
            character = list(filter(lambda character: character.name == name, possible_characters))  # get character

            if character:  # check if there is a character with the given name
                character_possible = True  # character is in game

        if not character_possible:  # check if character cannot be picked
            return responses.not_found("character")

        game.possible_characters = list(map(lambda character: ClassCharacter(database_object=character), possible_characters))  # add deck of possible characters to game object

        removed_characters = removed_characters_db.query.filter_by(game_uuid=game_uuid).all()  # get removed characters in game

        game.removed_characters = list(map(lambda character: ClassCharacter(database_object=character), removed_characters))  # add deck of removed characters to game object

        if possible_characters and game.amount_players == 2 and len(game.removed_characters) > 1:  # check if there are possible characters, two player game and atleaset 2 removed characters
            remove_character_possible = False

            remove_character = list(filter(lambda character: character.name == remove, possible_characters))  # get character to remove

            if remove_character:  # check if there is a character with given name
                remove_character_possible = True  # character is in game

            if not remove_character_possible:  # check if character cannot be removed
                return responses.not_found("remove character")

            if name == remove:  # check if character to pick is same as character to remove
                return responses.same_character()

        character = game.remove_character_from_possible_characters(name)  # remove character from possible characters for round

        success_write_character = database.write_row_to_db(characters_db(  # write character to database
            uuid=helpers.create_uuid(),
            name=character.name,
            open=character.open,
            assassinated=character.assassinated,
            robbed=character.robbed,
            built=character.built,
            income_received=character.income_received,
            player_uuid=player_uuid))

        if not success_write_character:  # check if failed to write to database
            return responses.error_writing_database("character")

        success_delete_possible_character = database.delete_row_from_db(possible_characters_db, character.uuid)  # delete character from possible characters in database

        if not success_delete_possible_character:  # check if failed to delete in database
            return responses.error_deleting_database("possible character")

        if game.amount_players == 2 and len(game.removed_characters) > 1:  # check if game has only 2 player and atleast 2 characters have been removed | game with 2 players requires each player to also remove a character for the round, where player two gets to remove the first character
            character = game.remove_character_from_possible_characters(remove)  # remove character from possible characters for round

            success_delete_possible_character = database.delete_row_from_db(possible_characters_db, character.uuid)  # delete character from possible characters in database

            if not success_delete_possible_character:  # check if failed to delete in database
                return responses.error_deleting_database("possible character")

        success_update_player = database.update_row_in_db(players_db, player_uuid, dict(select_expected=False))  # update select expected flag for current player in database

        if not success_update_player:  # check if failed to update database
            return responses.error_updating_database("player")

        selection_phase_finished = True

        selected_characters_count = 0

        players = players_db.query.filter_by(game_uuid=game_uuid).all()  # get players in game

        if not players:  # check if player does not exist
            return responses.not_found("players", True)

        players = list(map(lambda player: ClassPlayer(database_object=player), players))  # initialize player objects | don't add to game object because it messes with how the next seat is calculated

        for player in players:  # go through each player
            characters = characters_db.query.filter_by(player_uuid=player.uuid).all()  # get characters in player's hand

            if len(characters) != game.characters_per_player:  # check if player does not have the expected amount of characters
                selection_phase_finished = False

            selected_characters_count += len(characters)  # keep track of how many characters have already been selected

        if selection_phase_finished:  # check if the selection phase is finished
            for character in game.possible_characters:  # go through remaining possible characters
                success_write_removed_character = database.write_row_to_db(removed_characters_db(  # write character to database
                    uuid=helpers.create_uuid(),
                    name=character.name,
                    open=character.open,
                    assassinated=character.assassinated,
                    robbed=character.robbed,
                    built=character.built,
                    income_received=character.income_received,
                    game_uuid=game_uuid))

                if not success_write_removed_character:  # check if failed to write to database
                    return responses.error_writing_database("removed character")

                success_delete_possible_character = database.delete_row_from_db(possible_characters_db, character.uuid)  # delete character from possible characters in database

                if not success_delete_possible_character:  # check if failed to delete in database
                    return responses.error_deleting_database("possible character")

            game.state = ClassState.turn_phase.value  # update game to say it is ready to let each character perform their turn

            characters_complete_info = ClassCard().get_characters()  # get characters in game with complete information

            lowest_character = ClassCharacter(order=8, name=ClassCharacterName.warlord.value)  # keep track of character with the lowest order | start from the highest order number and work the way down

            for player in players:  # go through each player
                characters = characters_db.query.filter_by(player_uuid=player.uuid).all()  # get characters in player's hand

                characters = list(map(lambda character: ClassCharacter(database_object=character), characters))  # convert database object to class objects

                for character in characters:  # go through player's characters
                    character_complete_info = list(filter(lambda complete_character: complete_character.name == character.name, characters_complete_info))[0]  # get complete info on character

                    if character_complete_info.order < lowest_character.order:  # check if player's character has a lower order than the current lowest order
                        lowest_character = character_complete_info  # update the lowest character

            success_update_game = database.update_row_in_db(game_db, game_uuid, dict(state=game.state, character_turn=lowest_character.name))  # update database with the latest information about the game state

            if not success_update_game:  # check if database failed to update
                return responses.error_updating_database("game")


        else:  # there are players who still need to select characters
            next_seat_select_expected = game.players[0].seat + 1  # decide which player needs to pick a character next

            if next_seat_select_expected == game.amount_players:  # check if limit reached
                next_seat_select_expected = 0  # start back from seat 0

            player = players_db.query.filter_by(game_uuid=game_uuid, seat=next_seat_select_expected).first()  # get player in game who is expected to pick next

            if not player:  # check if player does not exist
                return responses.not_found("player")

            player_uuid = player.uuid  # get uuid of the next player | get value now before connection with database closes

            success_update_player = database.update_row_in_db(players_db, player_uuid, dict(select_expected=True))  # update select expected flag for next player in database

            if not success_update_player:  # check if failed to update database
                return responses.error_updating_database("player")

            if selected_characters_count == 6:  # check if player 7 needs to pick a character next | when game has 7 players, player 7 can pick between the removed facedown card and the possible character
                characters = list(filter(lambda character: character.open == False, game.removed_characters))  # get facedown removed characters

                for character in characters:  # go through characters
                    success_write_possible_character = database.write_row_to_db(possible_characters_db(  # write character to database
                        uuid=helpers.create_uuid(),
                        name=character.name,
                        open=character.open,
                        assassinated=character.assassinated,
                        robbed=character.robbed,
                        built=character.built,
                        income_received=character.income_received,
                        game_uuid=game_uuid))

                    if not success_write_possible_character:  # check if failed to write to database
                        return responses.error_writing_database("possible character")

                    success_delete_possible_character = database.delete_row_from_db(removed_characters_db, character.uuid)  # delete character from possible characters in database

                    if not success_delete_possible_character:  # check if failed to delete in database
                        return responses.error_deleting_database("removed character")

        return responses.no_content()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def keep_card(game_uuid, player_uuid, name):
    try:
        game = game_db.query.get(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        game = ClassGame(database_object=game)  # initialize game object

        if game.state != ClassState.turn_phase.value:  # check if game is in turn phase
            return responses.not_turn_phase()

        player = players_db.query.get(player_uuid)  # get player from database

        if not player:  # check if player does not exist
            return responses.not_found("player")

        game.players.append(ClassPlayer(database_object=player))  # add player to game object

        characters = characters_db.query.filter_by(player_uuid=player_uuid).all()  # get characters in player's hand

        if not characters:  # check if player has characters
            return responses.not_found("characters", True)

        character_in_hand = False

        characters = list(map(lambda character: ClassCharacter(database_object=character), characters))  # convert database objects to class objects

        character = list(filter(lambda character: character.name == game.character_turn, characters))  # get character

        if character:  # check if there is a character with the given name
            character = character[0]  # get character from list
            character_in_hand = True  # character is in player's hand

        if not character_in_hand:  # check if character is not in player's hand
            return responses.not_character()

        if character.income_received:  # check if the character has already received an income
            return responses.already_income_received()

        drawn_cards = drawn_cards_db.query.filter_by(player_uuid=player_uuid).all()  # get drawn district cards

        if not drawn_cards:  # check if the player has not yet drawn cards | the player can't pick beteen cards that have not been drawn
            return responses.no_cards_drawn()

        drawn_cards = list(map(lambda card: ClassDeckDistrict(amount=card.amount, card=ClassDistrict(uuid=card.uuid, name=card.name)), drawn_cards))  # convert database objects to class objects

        cards_for_hand = list(filter(lambda drawn_card: drawn_card.card.name == name, drawn_cards))  # get district for player's hand

        if not cards_for_hand:  # check if district cannot be kept
            return responses.not_found("district")

        cards_for_discard_pile = list(filter(lambda drawn_card: drawn_card.card.name != name, drawn_cards))  # filter cards where the name is different from the card for the player's hand

        if cards_for_hand[0].amount > 1:  # check if drawn cards have multiple copies of the same card
            amount_for_discard_pile = cards_for_hand[0].amount - 1  # keep 1 and the rest is for the discard pile

            cards_for_discard_pile.append(cards_for_hand[0])  # add card(s) to discard pile
            cards_for_discard_pile[0].amount = amount_for_discard_pile  # set right amount

            cards_for_hand[0].amount = 1  # set right amount

            # cards_for_discard_pile = cards_for_hand[1:]  # second card and further is for the discard pile
            # cards_for_hand = cards_for_hand[0]  # first card is for player's hand

        # deck_cards_for_discard_pile = game.aggregate_cards_by_name(cards_for_discard_pile)  # put cards in right format for update database function

        # deck_cards_for_hand = game.aggregate_cards_by_name(cards_for_hand)  # put cards in right format for update database function

        # TODO: fix issue where drawn cards table doesn't get cleared
        # TODO: fix issue where cards which already exist in table don't get an amount increase but instead just a new row

        __update_districts_in_database(drawn_cards_db, deck_discard_pile_db, drawn_cards, cards_for_discard_pile, game_uuid)  # write the cards for the discard pile to the deck_discard_pile table and update/remove the cards for the discard pile from the drawn_cards table

        __update_districts_in_database(drawn_cards_db, cards_db, drawn_cards, cards_for_hand, player_uuid, player_table=True)  # write the cards for the player's hand to the cards table and update/remove the cards for the player's hand from the drawn_cards table

        # updated_districts = []  # to avoid updating already updated districts (with the same value)
        # deleted_districts = []  # to avoid deleting already deleted districts

        # district_cards = {}
        # for card in cards_for_hand:  # go through
        #     if card.name not in district_cards.keys():  # check if card is not on new object
        #         district_cards[card.name] = ClassDeckDistrict(1, card)  # add card by amount to object
        #     else:  # card is in object
        #         new_deck_district = district_cards[card.name]  # get card from object
        #         new_deck_district.amount += 1  # increase amount
        #         district_cards[card.name] = new_deck_district  # update card in object

        # for _, deck_district in district_cards.items():  # go through each card in object
        #     success_write_card = database.write_row_to_db(drawn_cards_db(  # write card to database
        #         uuid=helpers.create_uuid(),
        #         name=deck_district.card.name,
        #         amount=deck_district.amount,
        #         player_uuid=player_uuid
        #     ))
        #
        #     if not success_write_card:  # check if failed to write to database
        #         return responses.error_writing_database("card")
        #
        #     amount = 0  # amount by default
        #
        #     district_by_amount = list(filter(lambda item: item.card.name.lower() == deck_district.card.name.lower(), game.deck_districts_by_amount))  # get current district from deck
        #
        #     if district_by_amount:  # check if there is a district
        #         amount = district_by_amount[0].amount  # get amount
        #
        #     if amount and deck_district.card.name not in updated_districts:  # check if district still in deck of districts and not yet updated in database
        #         updated_districts.append(deck_district.card.name)  # add district name to already updated districts
        #
        #         success_update_deck_districts = database.update_row_in_db(deck_districts_db, deck_district.card.uuid, dict(amount=amount))  # update card amount in deck of districts in database
        #
        #         if not success_update_deck_districts:  # check if failed to update database
        #             return responses.error_updating_database("deck of districts")
        #
        #     elif not amount and deck_district.card.name not in deleted_districts:  # district no longer in deck of districts and not yet deleted in database
        #         deleted_districts.append(deck_district.card.name)  # add district name to already deleted districts
        #
        #         success_delete_district = database.delete_row_from_db(deck_districts_db, deck_district.card.uuid)  # delete district from deck of districts in database
        #
        #         if not success_delete_district:  # check if failed to delete in database
        #             return responses.error_deleting_database("district")

        return responses.no_content()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()
