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

# TODO: add order by character order option for removed characters endpoint
# TODO: at end of game, don't clean up chaaracters etc, so players can observe game state at end of game
# TODO: removed characters are all closed when 4 players -> 2 should remain open
