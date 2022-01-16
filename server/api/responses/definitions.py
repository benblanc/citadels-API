def define_message(message):
    response = {
        "message": message
    }

    return response


def define_uuid(uuid):
    response = {
        "uuid": uuid
    }

    return response


def define_game(game):
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


def define_setting(setting):
    response = {
        "uuid": setting.uuid,
        "min_players": setting.min_players,
        "max_players": setting.max_players,
        "amount_starting_hand": setting.amount_starting_hand,
        "amount_starting_coins": setting.amount_starting_coins
    }

    return response


def define_player(player):
    response = {
        "uuid": player.uuid,
        "created": player.created.strftime('%Y-%m-%d %H:%M:%S'),
        "name": player.name,
        "hosting": player.hosting,
        "seat": player.seat,
        "coins": player.coins,
        "king": player.king,
        "protected": player.protected,
        "select_expected": player.select_expected
    }

    return response


def define_card(card):
    response = {
        "uuid": card.uuid,
        "name": card.name,
        "amount": card.amount
    }

    return response


def define_character(character):
    response = {
        "uuid": character.uuid,
        "name": character.name,
        "open": character.open,
        "assassinated": character.assassinated,
        "robbed": character.robbed,
        "built": character.built
    }

    return response
