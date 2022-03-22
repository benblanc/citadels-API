from api import db


class Cards(db.Model):
    __tablename__ = 'cards'
    uuid = db.Column(db.String(150), primary_key=True, nullable=False)
    name = db.Column(db.String(100))
    ability_used = db.Column(db.Boolean)
    amount = db.Column(db.Integer)
    player_uuid = db.Column(db.String(150), db.ForeignKey("players.uuid"), nullable=False, index=True)
