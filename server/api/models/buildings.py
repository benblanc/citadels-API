from api import db


class Buildings(db.Model):
    __tablename__ = 'buildings'
    uuid = db.Column(db.String(150), primary_key=True, nullable=False)
    name = db.Column(db.String(100))
    amount = db.Column(db.Integer)
    player_uuid = db.Column(db.String(150), db.ForeignKey("player.uuid"), nullable=False, index=True)
