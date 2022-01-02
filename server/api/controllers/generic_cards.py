import logging, traceback

from api.classes import card

import api.responses as responses

from api.validation import query


def apply_query(cards, sort_order, order_by, limit, offset, options_order_by):
    try:
        default_sort_order = False  # 'asc' = False | 'desc' = True
        default_order_by = 'name'
        default_limit = len(cards)
        default_offset = 0

        invalid_query = query.validate_query(sort_order, order_by, limit, offset, options_order_by)

        if invalid_query:
            return responses.conflict(invalid_query)

        if sort_order:  # check if not none
            if sort_order == 'asc':
                default_sort_order = False
            elif sort_order == 'desc':
                default_sort_order = True

        if order_by:  # check if not none
            default_order_by = order_by

        if limit:  # check if not none
            default_limit = limit

        if offset:  # check if not none
            default_offset = offset

        # apply order by and sort order
        if default_order_by == 'color':
            cards = sorted(cards, key=lambda card: card.color, reverse=default_sort_order)
        elif default_order_by == 'name':
            cards = sorted(cards, key=lambda card: card.name, reverse=default_sort_order)
        elif default_order_by == 'order':
            cards = sorted(cards, key=lambda card: card.order, reverse=default_sort_order)

        cards = cards[default_offset:]  # apply offset

        cards = cards[:default_limit]  # apply limit | needs to be separate from offset slice so limit value will not be used as index position

        return responses.success_get_generic_cards(cards)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def get_districts(sort_order, order_by, limit, offset):
    try:
        districts = card.ClassCard().get_districts()

        return apply_query(districts, sort_order, order_by, limit, offset, ['color', 'name'])

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def get_district(name):
    try:
        districts = card.ClassCard().get_districts()

        districts = list(filter(lambda district: district.name.lower() == name.lower(), districts))

        if districts:
            return responses.success_get_generic_card(districts)

        return responses.not_found()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def get_characters(sort_order, order_by, limit, offset):
    try:
        characters = card.ClassCard().get_characters()

        return apply_query(characters, sort_order, order_by, limit, offset, ['name', 'order'])

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()


def get_character(name):
    try:
        characters = card.ClassCard().get_characters()

        character = list(filter(lambda character: character.name.lower() == name.lower(), characters))

        if character:
            return responses.success_get_generic_card(character)

        return responses.not_found()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()
