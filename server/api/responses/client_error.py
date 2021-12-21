def bad_request(field):
    response = {
        "message": "The {field} value is required.".format(field=field)
    }

    return response, 400


def not_host():
    response = {
        "message": "The player making the request is not the host."
    }

    return response, 400


def not_enough_players():
    response = {
        "message": "The game does not have enough players to start."
    }

    return response, 400


def not_found():
    response = {
        "message": "The requested item is not found or does not exist."
    }

    return response, 404


def conflict(field):
    response = {
        "message": "The {field} value causes issues.".format(field=field)
    }

    return response, 409
