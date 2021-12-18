import logging, traceback

from api.classes import card

import api.responses as responses


def apply_query(cards, sort_order, limit, offset):
    try:
        default_sort_order = False  # 'asc' = False | 'desc' = True
        default_limit = len(cards)
        default_offset = 0

        if sort_order:  # check if sort order is not none
            if sort_order == 'asc':
                default_sort_order = False
            elif sort_order == 'desc':
                default_sort_order = True
            else:
                return responses.conflict('sort_order')

        cards = sorted(cards, key=lambda x: x.name, reverse=default_sort_order)  # apply sort order

        if offset:  # check if offset is not none
            if 0 < offset < len(cards):
                default_offset = offset
            else:
                return responses.conflict('offset')

        cards = cards[default_offset:]  # apply offset

        if limit:  # check if limit is not none
            if limit > 0:
                default_limit = limit
            else:
                return responses.conflict('limit')

        cards = cards[:default_limit]  # apply limit

        return responses.success_get_cards(cards)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.internal_server_error()


def get_districts(sort_order, limit, offset):
    try:
        districts = card.ClassCard().get_districts()

        return apply_query(districts, sort_order, limit, offset)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.internal_server_error()


def get_district(name):
    try:
        districts = card.ClassCard().get_districts()

        district = list(filter(lambda x: x.name.lower() == name.lower(), districts))

        if district:
            return responses.success_get_card(district)

        return responses.not_found()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.internal_server_error()


def get_characters(sort_order, limit, offset):
    try:
        characters = card.ClassCard().get_characters()

        return apply_query(characters, sort_order, limit, offset)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.internal_server_error()


def get_character(name):
    try:
        characters = card.ClassCard().get_characters()

        character = list(filter(lambda x: x.name.lower() == name.lower(), characters))

        if character:
            return responses.success_get_card(character)

        return responses.not_found()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.internal_server_error()
