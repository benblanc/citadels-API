from api.responses.definitions import *


def success_status():
    response = define_message("API is running.")

    return response, 200


def success_get_card(districts):
    response = list(map(lambda district: district.info, districts))[0]

    return response, 200


def success_get_cards(districts):
    response = list(map(lambda district: district.info, districts))

    return response, 200


def success_get_game(game):
    response = define_game(game)

    return response, 200


def success_get_games(games):
    response = list(map(lambda game: define_game(game), games))

    return response, 200


def success_get_player(player):
    response = define_player(player)

    return response, 200


def success_get_players(players):
    response = list(map(lambda player: define_player(player), players))

    return response, 200


def success_uuid(uuid):
    response = define_uuid(uuid)

    return response, 201


def no_content():
    return "", 204
