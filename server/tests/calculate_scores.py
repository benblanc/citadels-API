import requests, json, time

from tests.endpoints import *

from pprint import pprint

BASE_URL = "http://127.0.0.1:8080"

SLEEP_SECONDS = 0.10

if __name__ == '__main__':
    response_get_games = get_games(BASE_URL)

    if response_get_games.status_code != 200:
        exit(1)

    time.sleep(SLEEP_SECONDS)

    games = response_get_games.json()

    if not games:
        print("No games found!")
        exit(1)

    game_uuid = games[0]["uuid"]

    response_get_players = get_players(BASE_URL, game_uuid)

    if response_get_players.status_code != 200:
        exit(1)

    time.sleep(SLEEP_SECONDS)

    players = response_get_players.json()

    _players = {}

    for player in players:
        response_get_player_buildings = get_player_buildings(BASE_URL, game_uuid, player["uuid"])

        if response_get_player_buildings.status_code != 200:
            exit(1)

        time.sleep(SLEEP_SECONDS)

        player_buildings = response_get_player_buildings.json()

        player_buildings_complete_info = []

        for building in player_buildings:
            response_get_card = get_card(BASE_URL, building["name"])

            if response_get_card.status_code != 200:
                exit(1)

            time.sleep(SLEEP_SECONDS)

            card_full_info = response_get_card.json()

            for index in range(building["amount"]):
                player_buildings_complete_info.append(card_full_info)

        all_colors = list(set(map(lambda building: building["color"], player_buildings_complete_info)))  # get colors of buildings

        score = 0

        for building in player_buildings_complete_info:
            score += building["value"]

        if len(all_colors) == 5:
            score += 3

        if len(player_buildings_complete_info) >= 8:
            score += 2

        if player["city_first_completed"]:
            score += 2

        _players[player["name"]] = {
            "score_in_db": player["score"],
            "calculated_score": score
        }

    print("Calculation has finished!")

    pprint(_players)
