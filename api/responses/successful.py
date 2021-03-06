from api.responses.definitions import *


def success_status():
    response = define_message("API is running.")

    return response, 200


def success_get_generic_card(cards):
    response = list(map(lambda card: card.info, cards))[0]

    return response, 200


def success_get_generic_cards(cards):
    response = list(map(lambda card: card.info, cards))

    return response, 200


def success_get_game(game):
    response = define_game(game)

    return response, 200


def success_get_games(games):
    response = list(map(lambda game: define_game(game), games))

    return response, 200


def success_get_characters(characters):
    response = list(map(lambda character: define_character(character), characters))

    return response, 200


def success_get_districts(districts):
    response = list(map(lambda district: define_card(district), districts))

    return response, 200


def success_get_settings(settings):
    response = list(map(lambda setting: define_setting(setting), settings))

    return response, 200


def success_get_player(player):
    response = define_player(player)

    return response, 200


def success_get_players(players):
    response = list(map(lambda player: define_player(player), players))

    return response, 200


def success_get_cards(cards):
    response = list(map(lambda card: define_card(card), cards))

    return response, 200


def success_get_buildings(buildings):
    response = list(map(lambda building: define_card(building), buildings))

    return response, 200


def success_uuid(uuid):
    response = define_uuid(uuid)

    return response, 201


def no_content():
    return "", 204
