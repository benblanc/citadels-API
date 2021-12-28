def define_response_game(game):
    response = {
        "uuid": game.uuid,
        "created": game.created.strftime('%Y-%m-%d %H:%M:%S'),
        "name": game.name,
        "description": game.description,
        "state": game.state,
        "amount_players": game.amount_players,
        "characters_open": game.characters_open,
        "characters_closed": game.characters_closed,
        "characters_per_player": game.characters_per_player,
        "eight_districts_built": game.eight_districts_built,
        "round": game.round
    }

    return response


def define_response_player(player):
    response = {
        "uuid": player.uuid,
        "name": player.name,
        "hosting": player.hosting,
        "index": player.index,
        "coins": player.coins,
        "flag_king": player.flag_king,
        "flag_assassinated": player.flag_assassinated,
        "flag_robbed": player.flag_robbed,
        "flag_protected": player.flag_protected,
        "flag_built": player.flag_built
    }

    return response


def db_success_reading_game(game):
    response = define_response_game(game)

    return response, 200


def db_success_reading_all_games(games):
    response = list(map(lambda game: define_response_game(game), games))

    return response, 200


def db_success_reading_player(player):
    response = define_response_player(player)

    return response, 200


def db_success_reading_all_players(players):
    response = list(map(lambda player: define_response_player(player), players))

    return response, 200
