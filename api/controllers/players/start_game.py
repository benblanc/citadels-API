import logging, traceback

from copy import deepcopy

from api.classes.game import *

from api.models.cards import Cards as cards_db
from api.models.deck_districts import DeckDistricts as deck_districts_db
from api.models.game import Game as game_db
from api.models.players import Players as players_db

import api.responses as responses

from api.services import database

from api.utils import game_helpers, transactions


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

        game.deck_districts = game_helpers.get_shuffled_deck_districts(game_uuid)  # add districts to game object

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
            success_update_player = database.update_row_in_db(players_db, player.uuid, dict(seat=player.seat, coins=player.coins, crown=player.crown, select_expected=player.select_expected))  # update seat, amount of coins, crown and select expected flag for player in database

            if not success_update_player:  # check if failed to update database
                return responses.error_updating_database("player")

            cards = game.aggregate_cards_by_name(player.cards)  # update the amount per card

            error = game_helpers.update_districts_in_database(from_table=deck_districts_db, to_table=cards_db, cards=deepcopy(cards), uuid=player.uuid, from_deck_cards_by_amount=game.deck_districts_by_amount, player_table=True, to_table_name="card")

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
