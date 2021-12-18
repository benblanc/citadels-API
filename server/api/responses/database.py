def db_success_uuid(uuid):
    response = {
        "uuid": uuid
    }

    return response, 201


def db_success_reading_game(uuid, created, ):
    dict_result = {
        "created": created.strftime('%Y-%m-%d %H:%M:%S'),
        "uuid": uuid,
    }

    return dict_result, 200
