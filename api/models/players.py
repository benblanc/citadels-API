from api import db


class Players(db.Model):
    __tablename__ = 'players'
    uuid = db.Column(db.String(150), primary_key=True, nullable=False)
    created = db.Column(db.DateTime)
    name = db.Column(db.String(100))
    hosting = db.Column(db.Boolean)
    seat = db.Column(db.Integer)
    coins = db.Column(db.Integer)
    crown = db.Column(db.Boolean)
    protected = db.Column(db.Boolean)
    select_expected = db.Column(db.Boolean)
    city_first_completed = db.Column(db.Boolean)
    score = db.Column(db.Integer)
    game_uuid = db.Column(db.String(150), db.ForeignKey("game.uuid"), nullable=False, index=True)

    child1 = db.relationship("Cards", cascade="all, delete-orphan")
    child2 = db.relationship("Characters", cascade="all, delete-orphan")
    child3 = db.relationship("Buildings", cascade="all, delete-orphan")
