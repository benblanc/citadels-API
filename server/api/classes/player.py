class ClassPlayer:
    def __init__(self, uuid=None, created="", name="", hosting=False, index=0, coins=0, character=None, cards=None, buildings=None, king=False, protected=False):
        if character is None:
            character = []

        if cards is None:
            cards = []

        if buildings is None:
            buildings = []

        self.__uuid = uuid  # uuid of the player
        self.__created = created  # timestamp when player was created
        self.__name = name  # player name
        self.__hosting = hosting  # is player hosting the game
        self.__index = index  # player position
        self.__coins = coins  # amount of coins player has
        self.__character = character  # character(s) for current round
        self.__cards = cards  # distracts in hand
        self.__buildings = buildings  # districts built
        self.__king = king  # is player king
        self.__protected = protected  # is player protected from warlord

    @property
    def uuid(self):
        return self.__uuid

    @property
    def created(self):
        return self.__created

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def hosting(self):
        return self.__hosting

    @hosting.setter
    def hosting(self, value):
        self.__hosting = value

    @property
    def index(self):
        return self.__index

    @property
    def coins(self):
        return self.__coins

    @coins.setter
    def coins(self, value):
        self.__coins = value

    @property
    def character(self):
        return self.__character

    @character.setter
    def character(self, value):
        self.__character = value

    @property
    def cards(self):
        return self.__cards

    @cards.setter
    def cards(self, value):
        self.__cards = value

    @property
    def buildings(self):
        return self.__buildings

    @buildings.setter
    def buildings(self, value):
        self.__buildings = value

    @property
    def king(self):
        return self.__king

    @king.setter
    def king(self, value):
        self.__king = value

    @property
    def protected(self):
        return self.__protected

    @protected.setter
    def protected(self, value):
        self.__protected = value

    @property
    def info(self):

        character = []
        for item in self.__character:
            character.append(item.info)

        cards = []
        for item in self.__cards:
            cards.append(item.info)

        buildings = []
        for item in self.__buildings:
            buildings.append(item.info)

        info = {
            "uuid": self.__uuid,
            "created": self.__created,
            "name": self.__name,
            "hosting": self.__hosting,
            "index": self.__index,
            "coins": self.__coins,
            "character": character,
            "cards": cards,
            "buildings": buildings,
            "king": self.__king,
            "protected": self.__protected
        }

        return info

    def buildings_complete(self, necessary_building_amount):
        status = False

        if len(self.__buildings) == necessary_building_amount:
            status = True

        return status
