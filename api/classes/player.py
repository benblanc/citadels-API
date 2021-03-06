class ClassPlayer:
    def __init__(self, uuid=None, created="", name="", hosting=False, seat=0, gold=0, character=None, cards=None, buildings=None, crown=False, protected=False, select_expected=False, city_first_completed=False, score=0, database_object=None):
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
        self.__seat = seat  # player position
        self.__gold = gold  # amount of gold player has
        self.__character = character  # character(s) for current round
        self.__cards = cards  # distracts in hand
        self.__buildings = buildings  # districts built
        self.__crown = crown  # is player king
        self.__protected = protected  # is player protected from warlord
        self.__select_expected = select_expected  # is player expected to select a character
        self.__city_first_completed = city_first_completed  # is player the first one to have a completed city
        self.__score = score  # player's score

        if database_object:  # check if parameters contain a database object
            self.__uuid = database_object.uuid
            self.__created = database_object.created
            self.__name = database_object.name
            self.__hosting = database_object.hosting
            self.__seat = database_object.seat
            self.__gold = database_object.gold
            self.__crown = database_object.crown
            self.__protected = database_object.protected
            self.__select_expected = database_object.select_expected
            self.__city_first_completed = database_object.city_first_completed
            self.__score = database_object.score

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
    def seat(self):
        return self.__seat

    @seat.setter
    def seat(self, value):
        self.__seat = value

    @property
    def gold(self):
        return self.__gold

    @gold.setter
    def gold(self, value):
        self.__gold = value

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
    def crown(self):
        return self.__crown

    @crown.setter
    def crown(self, value):
        self.__crown = value

    @property
    def protected(self):
        return self.__protected

    @protected.setter
    def protected(self, value):
        self.__protected = value

    @property
    def select_expected(self):
        return self.__select_expected

    @select_expected.setter
    def select_expected(self, value):
        self.__select_expected = value

    @property
    def city_first_completed(self):
        return self.__city_first_completed

    @city_first_completed.setter
    def city_first_completed(self, value):
        self.__city_first_completed = value

    @property
    def score(self):
        return self.__score

    @score.setter
    def score(self, value):
        self.__score = value

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
            "seat": self.__seat,
            "gold": self.__gold,
            "character": character,
            "cards": cards,
            "buildings": buildings,
            "crown": self.__crown,
            "protected": self.__protected,
            "select_expected": self.__select_expected,
            "city_first_completed": self.__city_first_completed,
            "score": self.__score
        }

        return info

    def buildings_complete(self, necessary_building_amount):
        status = False

        if len(self.__buildings) == necessary_building_amount:
            status = True

        return status
