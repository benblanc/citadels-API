class ClassPlayer:
    def __init__(self, uuid=None, name="", hosting=False, index=0, coins=0, character=None, cards=None, buildings=None, flag_king=False, flag_assassinated=False, flag_robbed=False, flag_protected=False, flag_built=False):
        if character is None:
            character = []

        if cards is None:
            cards = []

        if buildings is None:
            buildings = []

        self.__uuid = uuid  # uuid of the player
        self.__name = name  # player name
        self.__hosting = hosting  # is player hosting the game
        self.__index = index  # player position
        self.__coins = coins  # amount of coins player has
        self.__character = character  # character(s) for current round
        self.__cards = cards  # distracts in hand
        self.__buildings = buildings  # districts built
        self.__flag_king = flag_king  # is player king
        self.__flag_assassinated = flag_assassinated  # is player assassinated
        self.__flag_robbed = flag_robbed  # is player robbed
        self.__flag_protected = flag_protected  # is player protected from warlord
        self.__flag_built = flag_built  # has the player built a district this turn

    @property
    def uuid(self):
        return self.__uuid

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
    def flag_king(self):
        return self.__flag_king

    @flag_king.setter
    def flag_king(self, value):
        self.__flag_king = value

    @property
    def flag_assassinated(self):
        return self.__flag_assassinated

    @flag_assassinated.setter
    def flag_assassinated(self, value):
        self.__flag_assassinated = value

    @property
    def flag_robbed(self):
        return self.__flag_robbed

    @flag_robbed.setter
    def flag_robbed(self, value):
        self.__flag_robbed = value

    @property
    def flag_protected(self):
        return self.__flag_protected

    @flag_protected.setter
    def flag_protected(self, value):
        self.__flag_protected = value

    @property
    def flag_built(self):
        return self.__flag_built

    @flag_built.setter
    def flag_built(self, value):
        self.__flag_built = value

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
            "hosting": self.__hosting,
            "index": self.__index,
            "name": self.__name,
            "coins": self.__coins,
            "character": character,
            "cards": cards,
            "buildings": buildings,
            "flag_king": self.__flag_king,
            "flag_assassinated": self.__flag_assassinated,
            "flag_robbed": self.__flag_robbed,
            "flag_protected": self.__flag_protected,
            "flag_built": self.__flag_built
        }

        return info

    def buildings_complete(self, necessary_building_amount):
        status = False

        if len(self.__buildings) == necessary_building_amount:
            status = True

        return status
