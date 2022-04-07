from api import db


class Settings(db.Model):
    __tablename__ = 'settings'
    uuid = db.Column(db.String(150), primary_key=True, nullable=False)
    min_players = db.Column(db.Integer)
    max_players = db.Column(db.Integer)
    amount_starting_hand = db.Column(db.Integer)
    amount_starting_gold = db.Column(db.Integer)
    game_uuid = db.Column(db.String(150), db.ForeignKey("game.uuid"), nullable=False, index=True)
