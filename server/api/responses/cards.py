def success_get_cards(districts):
    response = list(map(lambda x: x.info, districts))

    return response, 200


def success_get_card(district):
    response = list(map(lambda x: x.info, district))[0]

    return response, 200
