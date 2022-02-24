import logging, traceback

import api.responses as responses


def get_status():
    try:
        return responses.success_status()

    except Exception:
        logging.error(traceback.format_exc())
        return responses.error_handling_request()
