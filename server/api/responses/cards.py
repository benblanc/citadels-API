def success_get_cards(districts):
    response = list(map(lambda district: district.info, districts))

    return response, 200


def success_get_card(districts):
    response = list(map(lambda district: district.info, districts))[0]

    return response, 200
