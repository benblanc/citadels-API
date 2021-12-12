import json, logging, pickle, traceback

from api.classes import card

import api.responses as responses

from api.utils import helpers



def get_cards(sort_order, limit, offset):
    try:
        cards_object = card.ClassCard()

        characters = cards_object.get_characters()

        districts = cards_object.get_districts()

        logging.info(characters)

        response = list(map(lambda x: x.info, characters + districts))

        return response, 200

    except Exception:
        logging.error(traceback.format_exc())
        return "Something went wrong", 500


def get_districts(sort_order, limit, offset):
    try:
        cards_object = card.ClassCard()

        districts = cards_object.get_districts()

        response = list(map(lambda x: x.info, districts))

        return response, 200

    except Exception:
        logging.error(traceback.format_exc())
        return "Something went wrong", 500


def get_characters(sort_order, limit, offset):
    try:
        cards_object = card.ClassCard()

        characters = cards_object.get_characters()

        response = list(map(lambda x: x.info, characters))

        return response, 200

    except Exception:
        logging.error(traceback.format_exc())
        return "Something went wrong", 500
