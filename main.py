import logging, traceback

from api import app, db

from api.routes import buildings, cards, characters, deck_characters, deck_discard_pile, deck_districts, drawn_cards, game, players, possible_characters, removed_characters, settings, generic_cards, status
from api.models import buildings, cards, characters, deck_characters, deck_discard_pile, deck_districts, drawn_cards, game, players, possible_characters, removed_characters, settings

if __name__ == '__main__':
    try:
        db.create_all()  # create all defined database tables
        app.run(host='127.0.0.1', port=8080)

    except Exception:
        logging.error(traceback.format_exc())

# TODO: Add game log
