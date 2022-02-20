import requests, json, time, random

from tests.endpoints import *

from pprint import pprint

BASE_URL = "http://127.0.0.1:8080"

GAME_DESCRIPTION = "Test to simulate game and see how far it gets before breaking"
GAME_NAME = "Testing application"

NUMBER_OF_PLAYERS = 7

COINS_INCOME_LIMIT = 6

SLEEP_SECONDS = 0.10

EXIT_AFTER_GAME_CREATION = False
EXIT_AFTER_CHARACTER_SELECTION = True


def perform_selection(base_url, sleep_seconds, game_uuid):
    response_get_players = get_players(base_url, game_uuid)

    if response_get_players.status_code != 200:
        exit(1)

    time.sleep(sleep_seconds)

    players = response_get_players.json()

    expected_to_select = list(filter(lambda player: player["select_expected"] == True, players))

    if expected_to_select:  # check if someone still needs to pick a character
        player_expected_to_select = expected_to_select[0]

        response_get_possible_characters = get_possible_characters(base_url, game_uuid)

        if response_get_possible_characters.status_code != 200:
            exit(1)

        time.sleep(sleep_seconds)

        possible_characters = response_get_possible_characters.json()

        random_index = random.randint(0, len(possible_characters) - 1)

        keep_character = possible_characters[random_index]["name"]

        remove_character = ""

        if game["amount_players"] == 2:
            response_get_removed_characters = get_removed_characters(base_url, game_uuid)

            if response_get_removed_characters.status_code != 200:
                exit(1)

            time.sleep(sleep_seconds)

            removed_characters = response_get_removed_characters.json()

            if len(removed_characters) > 1:  # first player to pick doesn't remove a character
                remove_character = possible_characters[1]["name"]

        response_select_character = select_character(base_url, game_uuid, player_expected_to_select["uuid"], keep_character, remove_character)

        if response_select_character.status_code != 204:
            exit(1)

        time.sleep(sleep_seconds)


def perform_turn(base_url, sleep_seconds, game_uuid):
    response_get_players = get_players(base_url, game_uuid)

    if response_get_players.status_code != 200:
        exit(1)

    time.sleep(sleep_seconds)

    players = response_get_players.json()

    for player in players:
        response_get_player_characters = get_player_characters(base_url, game_uuid, player["uuid"])

        if response_get_player_characters.status_code != 200:
            exit(1)

        time.sleep(sleep_seconds)

        player_characters = response_get_player_characters.json()

        character_turn = list(filter(lambda character: character["name"] == game["character_turn"], player_characters))

        if character_turn:  # check if player has the character who is expected to play a turn
            character_expected_to_play = character_turn[0]

            response_get_character = get_character(base_url, character_expected_to_play["name"])

            if response_get_character.status_code != 200:
                exit(1)

            time.sleep(sleep_seconds)

            character = response_get_character.json()

            response_get_player_cards = get_player_cards(base_url, game_uuid, player["uuid"])

            if response_get_player_cards.status_code != 200:
                exit(1)

            time.sleep(sleep_seconds)

            player_cards = response_get_player_cards.json()

            response_get_player_buildings = get_player_buildings(base_url, game_uuid, player["uuid"])

            if response_get_player_buildings.status_code != 200:
                exit(1)

            time.sleep(sleep_seconds)

            player_buildings = response_get_player_buildings.json()

            player_building_names = list(map(lambda building: building["name"], player_buildings))

            cards_player_can_build = []
            for card in player_cards:
                if card["name"] not in player_building_names:  # check if not already built
                    response_get_card = get_card(base_url, card["name"])

                    if response_get_card.status_code != 200:
                        exit(1)

                    time.sleep(sleep_seconds)

                    card_full_info = response_get_card.json()

                    if player["coins"] >= card_full_info["coins"]:  # check if affordable
                        cards_player_can_build.append(card["name"])

            if not character_expected_to_play["income_received"]:  # check if character has not yet received an income
                if player["coins"] < COINS_INCOME_LIMIT:
                    response_receive_coins = receive_coins(base_url, game_uuid, player["uuid"])

                    if response_receive_coins.status_code != 204:
                        exit(1)

                    time.sleep(sleep_seconds)

                else:
                    response_draw_cards = draw_cards(base_url, game_uuid, player["uuid"])

                    if response_draw_cards.status_code != 204:
                        exit(1)

                    time.sleep(sleep_seconds)

                    response_get_drawn_cards = get_drawn_cards(base_url, game_uuid, player["uuid"])

                    if response_get_drawn_cards.status_code != 200:
                        exit(1)

                    time.sleep(sleep_seconds)

                    drawn_cards = response_get_drawn_cards.json()

                    response_keep_card = keep_card(base_url, game_uuid, player["uuid"], drawn_cards[0]["name"])

                    if response_keep_card.status_code != 204:
                        exit(1)

                    time.sleep(sleep_seconds)

            elif character_expected_to_play["income_received"] and character_expected_to_play["built"] < character["max_built"] and cards_player_can_build:  # check if character has received an income, building limit not yet reached and there are districts the player can actually build
                response_build = build(base_url, game_uuid, player["uuid"], cards_player_can_build[0])

                if response_build.status_code != 204:
                    exit(1)

                time.sleep(sleep_seconds)

            else:  # nothing else to do so end turn
                response_end_turn = end_turn(base_url, game_uuid, player["uuid"])

                if response_end_turn.status_code != 204:
                    exit(1)

                time.sleep(sleep_seconds)


if __name__ == '__main__':
    response_create_game = create_game(BASE_URL, GAME_DESCRIPTION, GAME_NAME)

    if response_create_game.status_code != 201:
        exit(1)

    time.sleep(SLEEP_SECONDS)

    game_uuid = response_create_game.json()["uuid"]

    player_name = "Wubby"

    for index in range(NUMBER_OF_PLAYERS):
        response_join_game = join_game(BASE_URL, game_uuid, player_name + " " + str(index))

        if response_join_game.status_code != 201:
            exit(1)

        time.sleep(SLEEP_SECONDS)

    response_get_players = get_players(BASE_URL, game_uuid)

    if response_get_players.status_code != 200:
        exit(1)

    time.sleep(SLEEP_SECONDS)

    players = response_get_players.json()

    host = list(filter(lambda player: player["hosting"] == True, players))[0]

    response_start_game = start_game(BASE_URL, game_uuid, host["uuid"])

    if response_start_game.status_code != 204:
        exit(1)

    time.sleep(SLEEP_SECONDS)

    response_get_game = get_game(BASE_URL, game_uuid)

    if response_get_game.status_code != 200:
        exit(1)

    time.sleep(SLEEP_SECONDS)

    game = response_get_game.json()

    if EXIT_AFTER_GAME_CREATION:
        print("EXIT_AFTER_GAME_CREATION")
        exit(0)

    while game["state"] != "finished":
        if game["state"] == "selection_phase":
            perform_selection(BASE_URL, SLEEP_SECONDS, game_uuid)

        if game["state"] == "turn_phase":
            if EXIT_AFTER_CHARACTER_SELECTION:
                print("EXIT_AFTER_CHARACTER_SELECTION")
                exit(0)

            perform_turn(BASE_URL, SLEEP_SECONDS, game_uuid)

        response_get_game = get_game(BASE_URL, game_uuid)

        if response_get_game.status_code != 200:
            exit(1)

        time.sleep(SLEEP_SECONDS)

        game = response_get_game.json()

    print("Game has finished!")
