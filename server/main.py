import logging, traceback

from api import app

from api.routes import status, cards

if __name__ == '__main__':
    try:
        app.run(host='127.0.0.1', port=8080)

    except Exception:
        logging.error(traceback.format_exc())
