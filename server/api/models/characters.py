from api import db


class Characters(db.Model):
    __tablename__ = 'characters'
    uuid = db.Column(db.String(150), primary_key=True, nullable=False)
    name = db.Column(db.String(100))
    player_uuid = db.Column(db.String(150), db.ForeignKey("player.uuid"), nullable=False, index=True)
