from api import db


class DeckDiscardPile(db.Model):
    __tablename__ = 'deck_discard_pile'
    uuid = db.Column(db.String(150), primary_key=True, nullable=False)
    name = db.Column(db.String(100))
    amount = db.Column(db.Integer)
    game_uuid = db.Column(db.String(150), db.ForeignKey("game.uuid"), nullable=False, index=True)
