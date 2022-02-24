from api import db


class Game(db.Model):
    __tablename__ = 'game'
    uuid = db.Column(db.String(150), primary_key=True, nullable=False)
    created = db.Column(db.DateTime)
    name = db.Column(db.String(100))
    description = db.Column(db.String(100))
    state = db.Column(db.String(100))
    amount_players = db.Column(db.Integer)
    character_turn = db.Column(db.String(100))
    round = db.Column(db.Integer)

    child1 = db.relationship("Settings", cascade="all, delete-orphan")
    child2 = db.relationship("Players", cascade="all, delete-orphan")
    child3 = db.relationship("DeckDistricts", cascade="all, delete-orphan")
    child4 = db.relationship("DeckDiscardPile", cascade="all, delete-orphan")
    child5 = db.relationship("DeckCharacters", cascade="all, delete-orphan")
    child6 = db.relationship("PossibleCharacters", cascade="all, delete-orphan")
    child7 = db.relationship("RemovedCharacters", cascade="all, delete-orphan")
