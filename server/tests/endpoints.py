import requests, json, time

from pprint import pprint


def log_response(response):
    print("request url: ", response.request.url)
    print("request body:")

    content = ""
    if response.request.body:  # check if there is content
        content = json.loads(response.request.body.decode('utf8'))

    pprint(content)
    print("-" * 50)
    print("response status code: ", response.status_code)
    print("response body:")

    content = response.text
    if response.text:  # check if there is content
        content = response.json()

    pprint(content)
    print("=" * 100)


def create_game(base_url, description, name):
    payload = {
        "description": description,
        "name": name
    }

    response = requests.post(url=base_url + "/game/action.create", json=payload)

    log_response(response)

    return response


def join_game(base_url, game_uuid, name):
    payload = {
        "name": name
    }

    response = requests.post(url=base_url + "/game/" + game_uuid + "/action.join", json=payload)

    log_response(response)

    return response


def get_players(base_url, game_uuid):
    response = requests.get(url=base_url + "/game/" + game_uuid + "/players")

    log_response(response)

    return response


def start_game(base_url, game_uuid, player_uuid):
    response = requests.post(url=base_url + "/game/" + game_uuid + "/players/" + player_uuid + "/action.start")

    log_response(response)

    return response


def get_games(base_url):
    response = requests.get(url=base_url + "/game")

    log_response(response)

    return response


def get_game(base_url, game_uuid):
    response = requests.get(url=base_url + "/game/" + game_uuid)

    log_response(response)

    return response


def get_possible_characters(base_url, game_uuid):
    response = requests.get(url=base_url + "/game/" + game_uuid + "/possible_characters")

    log_response(response)

    return response


def select_character(base_url, game_uuid, player_uuid, name, remove):
    payload = {
        "name": name,
        "remove": remove
    }

    response = requests.post(url=base_url + "/game/" + game_uuid + "/players/" + player_uuid + "/action.select", json=payload)

    log_response(response)

    return response


def get_removed_characters(base_url, game_uuid):
    response = requests.get(url=base_url + "/game/" + game_uuid + "/removed_characters")

    log_response(response)

    return response


def get_player_characters(base_url, game_uuid, player_uuid):
    response = requests.get(url=base_url + "/game/" + game_uuid + "/players/" + player_uuid + "/characters")

    log_response(response)

    return response


def receive_coins(base_url, game_uuid, player_uuid):
    response = requests.post(url=base_url + "/game/" + game_uuid + "/players/" + player_uuid + "/action.receive_coins")

    log_response(response)

    return response


def draw_cards(base_url, game_uuid, player_uuid):
    response = requests.post(url=base_url + "/game/" + game_uuid + "/players/" + player_uuid + "/action.draw_cards")

    log_response(response)

    return response


def keep_card(base_url, game_uuid, player_uuid, name):
    payload = {
        "name": name,
    }

    response = requests.post(url=base_url + "/game/" + game_uuid + "/players/" + player_uuid + "/action.keep_card", json=payload)

    log_response(response)

    return response


def get_drawn_cards(base_url, game_uuid, player_uuid):
    response = requests.get(url=base_url + "/game/" + game_uuid + "/players/" + player_uuid + "/drawn_cards")

    log_response(response)

    return response


def end_turn(base_url, game_uuid, player_uuid):
    response = requests.post(url=base_url + "/game/" + game_uuid + "/players/" + player_uuid + "/action.end_turn")

    log_response(response)

    return response


def get_character(base_url, name):
    response = requests.get(url=base_url + "/cards/characters/" + name)

    log_response(response)

    return response


def build(base_url, game_uuid, player_uuid, name):
    payload = {
        "name": name,
    }

    response = requests.post(url=base_url + "/game/" + game_uuid + "/players/" + player_uuid + "/action.build", json=payload)

    log_response(response)

    return response


def get_player_cards(base_url, game_uuid, player_uuid):
    response = requests.get(url=base_url + "/game/" + game_uuid + "/players/" + player_uuid + "/cards")

    log_response(response)

    return response


def get_player_buildings(base_url, game_uuid, player_uuid):
    response = requests.get(url=base_url + "/game/" + game_uuid + "/players/" + player_uuid + "/buildings")

    log_response(response)

    return response


def get_card(base_url, name):
    response = requests.get(url=base_url + "/cards/districts/" + name)

    log_response(response)

    return response
