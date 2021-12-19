import logging, traceback

from api import app, db

from api.routes import cards, game, status
from api.models import buildings, cards, characters, deck_characters, deck_discard_pile, deck_districts, game, players, possible_characters, removed_characters, settings

db.create_all()  # create all defined database tables

if __name__ == '__main__':
    try:
        app.run(host='127.0.0.1', port=8080)

    except Exception:
        logging.error(traceback.format_exc())
