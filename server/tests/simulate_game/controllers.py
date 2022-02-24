import time, random

from tests import endpoints

BASE_URL = "http://127.0.0.1:8080"

SLEEP_SECONDS = 0.10


def create_game(game_description, game_name):
    response_create_game = endpoints.create_game(BASE_URL, game_description, game_name)

    if response_create_game.status_code != 201:
        exit(1)

    time.sleep(SLEEP_SECONDS)

    return response_create_game.json()


def join_game(game_uuid, player_name):
    response_join_game = endpoints.join_game(BASE_URL, game_uuid, player_name)

    if response_join_game.status_code != 201:
        exit(1)

    time.sleep(SLEEP_SECONDS)

    return response_join_game.json()


def get_players(game_uuid):
    response_get_players = endpoints.get_players(BASE_URL, game_uuid)

    if response_get_players.status_code != 200:
        exit(1)

    time.sleep(SLEEP_SECONDS)

    return response_get_players.json()


def start_game(game_uuid, player_uuid):
    response_start_game = endpoints.start_game(BASE_URL, game_uuid, player_uuid)

    if response_start_game.status_code != 204:
        exit(1)

    time.sleep(SLEEP_SECONDS)


def get_game(game_uuid):
    response_get_game = endpoints.get_game(BASE_URL, game_uuid)

    if response_get_game.status_code != 200:
        exit(1)

    time.sleep(SLEEP_SECONDS)

    return response_get_game.json()


def get_possible_characters(game_uuid):
    response_get_possible_characters = endpoints.get_possible_characters(BASE_URL, game_uuid)

    if response_get_possible_characters.status_code != 200:
        exit(1)

    time.sleep(SLEEP_SECONDS)

    return response_get_possible_characters.json()


def get_removed_characters(game_uuid):
    response_get_removed_characters = endpoints.get_removed_characters(BASE_URL, game_uuid)

    if response_get_removed_characters.status_code != 200:
        exit(1)

    time.sleep(SLEEP_SECONDS)

    return response_get_removed_characters.json()


def select_character(game_uuid, player_uuid, keep_character, remove_character):
    response_select_character = endpoints.select_character(BASE_URL, game_uuid, player_uuid, keep_character, remove_character)

    if response_select_character.status_code != 204:
        exit(1)

    time.sleep(SLEEP_SECONDS)


def receive_coins(game_uuid, player_uuid):
    response_receive_coins = endpoints.receive_coins(BASE_URL, game_uuid, player_uuid)

    if response_receive_coins.status_code != 204:
        exit(1)

    time.sleep(SLEEP_SECONDS)


def draw_cards(game_uuid, player_uuid):
    response_draw_cards = endpoints.draw_cards(BASE_URL, game_uuid, player_uuid)

    if response_draw_cards.status_code != 204:
        exit(1)

    time.sleep(SLEEP_SECONDS)


def get_drawn_cards(game_uuid, player_uuid):
    response_get_drawn_cards = endpoints.get_drawn_cards(BASE_URL, game_uuid, player_uuid)

    if response_get_drawn_cards.status_code != 200:
        exit(1)

    time.sleep(SLEEP_SECONDS)

    return response_get_drawn_cards.json()


def keep_card(game_uuid, player_uuid, drawn_card):
    response_keep_card = endpoints.keep_card(BASE_URL, game_uuid, player_uuid, drawn_card)

    if response_keep_card.status_code != 204:
        exit(1)

    time.sleep(SLEEP_SECONDS)


def build(game_uuid, player_uuid, district):
    response_build = endpoints.build(BASE_URL, game_uuid, player_uuid, district)

    if response_build.status_code != 204:
        exit(1)

    time.sleep(SLEEP_SECONDS)


def use_ability(game_uuid, player_uuid, main=False, character_name=None, districts_name=None, other_player_uuid=None):
    response_use_ability = endpoints.use_ability(BASE_URL, game_uuid, player_uuid, main=main, character_name=character_name, districts_name=districts_name, other_player_uuid=other_player_uuid)

    if response_use_ability.status_code != 204:
        exit(1)

    time.sleep(SLEEP_SECONDS)


def get_player_characters(game_uuid, player_uuid):
    response_get_player_characters = endpoints.get_player_characters(BASE_URL, game_uuid, player_uuid)

    if response_get_player_characters.status_code != 200:
        exit(1)

    time.sleep(SLEEP_SECONDS)

    return response_get_player_characters.json()


def get_character(name):
    response_get_character = endpoints.get_character(BASE_URL, name)

    if response_get_character.status_code != 200:
        exit(1)

    time.sleep(SLEEP_SECONDS)

    return response_get_character.json()


def get_player_cards(game_uuid, player_uuid):
    response_get_player_cards = endpoints.get_player_cards(BASE_URL, game_uuid, player_uuid)

    if response_get_player_cards.status_code != 200:
        exit(1)

    time.sleep(SLEEP_SECONDS)

    return response_get_player_cards.json()


def get_player_buildings(game_uuid, player_uuid):
    response_get_player_buildings = endpoints.get_player_buildings(BASE_URL, game_uuid, player_uuid)

    if response_get_player_buildings.status_code != 200:
        exit(1)

    time.sleep(SLEEP_SECONDS)

    return response_get_player_buildings.json()


def get_card(name):
    response_get_card = endpoints.get_card(BASE_URL, name)

    if response_get_card.status_code != 200:
        exit(1)

    time.sleep(SLEEP_SECONDS)

    return response_get_card.json()


def get_characters():
    response_get_characters = endpoints.get_characters(BASE_URL)

    if response_get_characters.status_code != 200:
        exit(1)

    time.sleep(SLEEP_SECONDS)

    return response_get_characters.json()


def end_turn(game_uuid, player_uuid):
    response_end_turn = endpoints.end_turn(BASE_URL, game_uuid, player_uuid)

    if response_end_turn.status_code != 204:
        exit(1)

    time.sleep(SLEEP_SECONDS)


def get_player(game_uuid, player_uuid):
    response_get_player = endpoints.get_player(BASE_URL, game_uuid, player_uuid)

    if response_get_player.status_code != 200:
        exit(1)

    time.sleep(SLEEP_SECONDS)

    return response_get_player.json()
