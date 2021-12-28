def success_uuid(uuid):
    response = {
        "uuid": uuid
    }

    return response, 200


def success_uuid_entity_created(uuid):
    response = {
        "uuid": uuid
    }

    return response, 201


def no_content():
    return "", 204
