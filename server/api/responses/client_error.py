def bad_request(field):
    response = {
        "message": "The {field} value is required.".format(field=field)
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
