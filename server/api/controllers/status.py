import logging, traceback

import api.responses as responses


def get_status():
    try:
        return responses.status_success_reading()

    except Exception:
        logging.error(traceback.format_exc())
        # return responses.internal_server_error("5xS01", traceback.format_exc())
        return "Something went wrong", 500
