from api import db


class DeckCharacters(db.Model):
    __tablename__ = 'deck_characters'
    uuid = db.Column(db.String(150), primary_key=True, nullable=False)
    name = db.Column(db.String(100))
    open = db.Column(db.Boolean)
    game_uuid = db.Column(db.String(150), db.ForeignKey("game.uuid"), nullable=False, index=True)
