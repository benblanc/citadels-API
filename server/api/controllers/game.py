import logging, traceback, random

# from api.classes import card, game, player
from api.classes.card import *
from api.classes.game import *
from api.classes.player import *

from api.models.game import Game as game_db
from api.models.settings import Settings as settings_db
from api.models.deck_districts import DeckDistricts as deck_districts_db
from api.models.deck_characters import DeckCharacters as deck_characters_db
from api.models.players import Players as players_db
from api.models.cards import Cards as cards_db

import api.responses as responses

from api.services import database

from api.utils import helpers

from api.validation import query

from pprint import pprint


def get_games(sort_order, order_by, limit, offset):
    try:
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
            sort = game_db.created
        elif default_order_by == 'name':
            sort = game_db.name

        if default_sort_order == 'asc':
            sort = sort.asc()
        elif default_sort_order == 'desc':
            sort = sort.desc()

        if default_limit == 0:
            games = game_db.query.order_by(sort).offset(default_offset).all()
        else:
            games = game_db.query.order_by(sort).limit(default_limit).offset(default_offset).all()

        return responses.success_get_games(games)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def get_game(game_uuid):
    try:
        game = game_db.query.get(game_uuid)

        if game:
            return responses.success_get_game(game)

        return responses.not_found()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def create_game(name, description):
    try:
        new_game = ClassGame(helpers.create_uuid(), helpers.create_timestamp(), name, description, ClassState.created.value)

        success_write_game = database.write_row_to_db(game_db(
            uuid=new_game.uuid,
            created=new_game.created,
            name=new_game.name,
            description=new_game.description,
            state=new_game.state,
            amount_players=new_game.amount_players,
            characters_open=new_game.characters_open,
            characters_closed=new_game.characters_closed,
            characters_per_player=new_game.characters_per_player,
            eight_districts_built=new_game.eight_districts_built,
            round=new_game.round))

        if not success_write_game:
            return responses.error_writing_database("game")

        success_write_settings = database.write_row_to_db(settings_db(
            uuid=helpers.create_uuid(),
            min_players=new_game.settings.min_players,
            max_players=new_game.settings.max_players,
            amount_starting_hand=new_game.settings.amount_starting_hand,
            amount_starting_coins=new_game.settings.amount_starting_coins,
            game_uuid=new_game.uuid))

        if not success_write_settings:
            return responses.error_writing_database("settings")

        new_game.deck_districts = ClassCard().get_districts(False)

        success_write_deck_districts = []
        for district in new_game.deck_districts:
            success_write_deck_districts.append(database.write_row_to_db(deck_districts_db(
                uuid=helpers.create_uuid(),
                name=district.card.name,
                amount=district.amount,
                game_uuid=new_game.uuid)))

        if False in success_write_deck_districts:
            return responses.error_writing_database("deck of districts")

        new_game.deck_characters = ClassCard().get_characters()

        success_write_deck_characters = []
        for character in new_game.deck_characters:
            success_write_deck_characters.append(database.write_row_to_db(deck_characters_db(
                uuid=helpers.create_uuid(),
                name=character.name,
                game_uuid=new_game.uuid)))

        if False in success_write_deck_characters:
            return responses.error_writing_database("deck of characters")

        return responses.success_uuid(new_game.uuid)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def join_game(game_uuid, name):
    try:
        game = game_db.query.get(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        amount_players = game.amount_players  # get amount of players before connection with database closes

        settings = settings_db.query.filter_by(game_uuid=game_uuid).first()  # get settings from database

        if not settings:  # check if game settings do not exist
            return responses.not_found("settings", True)

        # TODO: I could join when game was already busy, find out why and fix it

        if amount_players == settings.max_players:  # check if there are already enough players
            return responses.enough_players()

        hosting = True  # assume new player is hosting

        players = players_db.query.filter_by(game_uuid=game_uuid).all()  # get players in game

        if players:  # check if there are players
            host = list(filter(lambda player: player.hosting == True, players))  # get host

            if host:  # check if there is a host
                hosting = False  # new player will not host the game

        new_player = ClassPlayer(helpers.create_uuid(), name, hosting)

        success_write_player = database.write_row_to_db(players_db(
            uuid=new_player.uuid,
            name=new_player.name,
            hosting=new_player.hosting,
            index=new_player.index,
            coins=new_player.coins,
            flag_king=new_player.flag_king,
            flag_assassinated=new_player.flag_assassinated,
            flag_robbed=new_player.flag_robbed,
            flag_protected=new_player.flag_protected,
            flag_built=new_player.flag_built,
            game_uuid=game_uuid
        ))

        if not success_write_player:
            return responses.error_writing_database("player")

        success_update_game = database.update_row_in_db(game_db, game_uuid, dict(amount_players=len(players) + 1))  # update player count for game

        if not success_update_game:
            return responses.error_updating_database("game")

        return responses.success_uuid(new_player.uuid)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def start_game(game_uuid, player_uuid):
    try:
        game = game_db.query.get(game_uuid)  # get game from database

        if not game:  # check if game does not exist
            return responses.not_found("game")

        game = ClassGame(uuid=game_uuid, created=game.created, name=game.name, description=game.description, state=game.state, amount_players=game.amount_players, characters_open=game.characters_open, characters_closed=game.characters_closed, characters_per_player=game.characters_per_player, eight_districts_built=game.eight_districts_built, round=game.round)  # initialize game object

        player = players_db.query.get(player_uuid)  # get player from database

        if not player:  # check if player does not exist
            return responses.not_found("player")

        if not player.hosting:  # check if the player is not hosting the game
            return responses.not_host()

        settings = settings_db.query.filter_by(game_uuid=game_uuid).first()  # get settings from database

        if not settings:  # check if game settings do not exist
            return responses.not_found("settings", True)

        game.settings = ClassSettings(min_players=settings.min_players, max_players=settings.max_players, amount_starting_hand=settings.amount_starting_hand, amount_starting_coins=settings.amount_starting_coins)  # add settings to game object

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

        deck_characters = deck_characters_db.query.filter_by(game_uuid=game_uuid).all()  # get deck of characters in game

        characters = list(map(lambda character: ClassCharacter(uuid=character.uuid, name=character.name), deck_characters))  # get characters as class objects

        random.shuffle(characters)  # shuffle district cards

        game.deck_characters = characters  # add characters to game object

        players = players_db.query.filter_by(game_uuid=game_uuid).all()  # get players in game

        if not players:  # check if there are no players
            return responses.not_found("players", True)

        game.players = list(map(lambda player: ClassPlayer(uuid=player.uuid, name=player.name, hosting=player.hosting, index=player.index, coins=player.coins, flag_king=player.flag_king, flag_assassinated=player.flag_assassinated, flag_robbed=player.flag_robbed, flag_protected=player.flag_protected, flag_built=player.flag_built), players))  # add players to game object

        game.set_starting_coins_per_player()  # give each player coins to start with

        game.set_starting_hand_per_player()  # give each player district cards to start with

        game.set_starting_king()  # let a random player start as the king

        game.set_character_division()  # define how many characters per player and how many are open or closed on the field

        updated_districts = []  # to avoid updating already updated districts (with the same value)
        deleted_districts = []  # to avoid deleting already deleted districts

        for player in game.players:  # go through each player
            success_update_player = database.update_row_in_db(players_db, player.uuid, dict(coins=player.coins, flag_king=player.flag_king))  # update amount of coins and king flag for player in database

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

        game.state = ClassState.dividing.value  # update game to say it is ready to divide characters per player

        success_update_game = database.update_row_in_db(game_db, game_uuid, dict(state=game.state, characters_open=game.characters_open, characters_closed=game.characters_closed, characters_per_player=game.characters_per_player))  # update database with the latest information about the game state

        if not success_update_game:  # check if database failed to update
            return responses.error_updating_database("game")

        return responses.no_content()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()
