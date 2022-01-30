import requests, json, time

from pprint import pprint

BASE_URL = "http://127.0.0.1:8080"

BASE_HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json"
}

NUMBER_OF_PLAYERS = 4

SLEEP_SECONDS = 0.10


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


def create_game(description, name):
    payload = {
        "description": description,
        "name": name
    }

    response = requests.post(url=BASE_URL + "/game/action.create", json=payload)

    log_response(response)

    return response


def join_game(game_uuid, name):
    payload = {
        "name": name
    }

    response = requests.post(url=BASE_URL + "/game/" + game_uuid + "/action.join", json=payload)

    log_response(response)

    return response


def get_players(game_uuid):
    response = requests.get(url=BASE_URL + "/game/" + game_uuid + "/players")

    log_response(response)

    return response


def start_game(game_uuid, player_uuid):
    response = requests.post(url=BASE_URL + "/game/" + game_uuid + "/players/" + player_uuid + "/action.start")

    log_response(response)

    return response


def get_game(game_uuid):
    response = requests.get(url=BASE_URL + "/game/" + game_uuid)

    log_response(response)

    return response


def get_possible_characters(game_uuid):
    response = requests.get(url=BASE_URL + "/game/" + game_uuid + "/possible_characters")

    log_response(response)

    return response


def select_character(game_uuid, player_uuid, name, remove):
    payload = {
        "name": name,
        "remove": remove
    }

    response = requests.post(url=BASE_URL + "/game/" + game_uuid + "/players/" + player_uuid + "/action.select", json=payload)

    log_response(response)

    return response


def get_removed_characters(game_uuid):
    response = requests.get(url=BASE_URL + "/game/" + game_uuid + "/removed_characters")

    log_response(response)

    return response


if __name__ == '__main__':
    game_description = "Test to simulate game and see how far it gets before breaking"
    game_name = "Testing application"

    response_create_game = create_game(game_description, game_name)

    if response_create_game.status_code != 201:
        exit(1)

    time.sleep(SLEEP_SECONDS)

    game_uuid = response_create_game.json()["uuid"]

    player_name = "Wubby"

    for index in range(NUMBER_OF_PLAYERS):
        response_join_game = join_game(game_uuid, player_name + " " + str(index))

        if response_join_game.status_code != 201:
            exit(1)

        time.sleep(SLEEP_SECONDS)

    response_get_players = get_players(game_uuid)

    if response_get_players.status_code != 200:
        exit(1)

    time.sleep(SLEEP_SECONDS)

    players = response_get_players.json()

    host = list(filter(lambda player: player["hosting"] == True, players))[0]

    response_start_game = start_game(game_uuid, host["uuid"])

    if response_start_game.status_code != 204:
        exit(1)

    time.sleep(SLEEP_SECONDS)

    response_get_game = get_game(game_uuid)

    if response_get_game.status_code != 200:
        exit(1)

    time.sleep(SLEEP_SECONDS)

    game = response_get_game.json()

    while game["state"] != "finished":
        if game["state"] == "selection_phase":
            response_get_players = get_players(game_uuid)

            if response_get_players.status_code != 200:
                exit(1)

            time.sleep(SLEEP_SECONDS)

            players = response_get_players.json()

            expected_to_select = list(filter(lambda player: player["select_expected"] == True, players))

            if expected_to_select:  # check if someone still needs to pick a character

                player_expected_to_select = expected_to_select[0]

                response_get_possible_characters = get_possible_characters(game_uuid)

                if response_get_possible_characters.status_code != 200:
                    exit(1)

                time.sleep(SLEEP_SECONDS)

                possible_characters = response_get_possible_characters.json()

                keep_character = possible_characters[0]["name"]

                remove_character = ""

                if game["amount_players"] == 2:
                    response_get_removed_characters = get_removed_characters(game_uuid)

                    if response_get_removed_characters.status_code != 200:
                        exit(1)

                    time.sleep(SLEEP_SECONDS)

                    removed_characters = response_get_removed_characters.json()

                    if len(removed_characters) > 1:  # first player to pick doesn't remove a character
                        remove_character = possible_characters[1]["name"]

                response_select_character = select_character(game_uuid, player_expected_to_select["uuid"], keep_character, remove_character)

                if response_select_character.status_code != 204:
                    exit(1)

                time.sleep(SLEEP_SECONDS)

        if game["state"] == "turn_phase":
            # game["state"] = "finished"
            break

        response_get_game = get_game(game_uuid)

        if response_get_game.status_code != 200:
            exit(1)

        time.sleep(SLEEP_SECONDS)

        game = response_get_game.json()

    print("Game has finished!")
