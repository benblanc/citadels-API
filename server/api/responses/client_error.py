from api.responses.definitions import *


def bad_request(field):
    response = define_message("The {field} value is required.".format(field=field))

    return response, 400


def not_host():
    response = define_message("The player making the request is not the host.")

    return response, 400


def not_enough_players():
    response = define_message("The game does not have enough players to start.")

    return response, 400


def enough_players():
    response = define_message("The game already has enough players to start.")

    return response, 400


def already_started():
    response = define_message("The game has already started.")

    return response, 400


def not_found(item="item", plural=False):
    message = "The requested {item} is not found or does not exist.".format(item=item)

    if plural:  # check if message needs to be plural
        message = "The requested {item} are not found or do not exist.".format(item=item)

    response = define_message(message)

    return response, 404


def conflict(field):
    response = define_message("The {field} value causes issues.".format(field=field))

    return response, 409
