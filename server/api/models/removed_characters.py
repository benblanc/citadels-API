from api import db


class RemovedCharacters(db.Model):
    __tablename__ = 'removed_characters'
    uuid = db.Column(db.String(150), primary_key=True, nullable=False)
    name = db.Column(db.String(100))
    open = db.Column(db.Boolean)
    assassinated = db.Column(db.Boolean)
    robbed = db.Column(db.Boolean)
    built = db.Column(db.Integer)
    income_received = db.Column(db.Boolean)
    game_uuid = db.Column(db.String(150), db.ForeignKey("game.uuid"), nullable=False, index=True)
