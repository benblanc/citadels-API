import logging, traceback

from api.classes import card

import api.responses as responses


def get_districts(sort_order, limit, offset):
    try:
        districts = card.ClassCard().get_districts()

        return apply_query(districts, sort_order, limit, offset)

    except Exception:
        logging.error(traceback.format_exc())
        return responses.internal_server_error()
