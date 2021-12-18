from api import db


class Players(db.Model):
    __tablename__ = 'players'
    uuid = db.Column(db.String(150), primary_key=True, nullable=False)
    name = db.Column(db.String(100))
    index = db.Column(db.Integer)
    coins = db.Column(db.Integer)
    flag_king = db.Column(db.Boolean)
    flag_assassinated = db.Column(db.Boolean)
    flag_robbed = db.Column(db.Boolean)
    flag_protected = db.Column(db.Boolean)
    flag_built = db.Column(db.Boolean)
    game_uuid = db.Column(db.String(150), db.ForeignKey("game.uuid"), nullable=False, index=True)

    child1 = db.relationship("Cards", cascade="all, delete-orphan")
    child2 = db.relationship("Characters", cascade="all, delete-orphan")
    child3 = db.relationship("Buildings", cascade="all, delete-orphan")
