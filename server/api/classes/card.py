class ClassDistrict:
    def __init__(self, uuid=None, name="", color="", coins=0, value=0, effect=None):
        self.__name = name
        self.__color = color
        self.__coins = coins
        self.__value = value
        self.__effect = effect
        self.__uuid = uuid

    def __eq__(self, other):  # override default equals behavior
        return self.__name == other.__name and self.__color == other.__color and self.__coins == other.__coins and self.__value == other.__value and self.__effect == other.__effect

    @property
    def uuid(self):
        return self.__uuid

    @property
    def name(self):
        return self.__name

    @property
    def color(self):
        return self.__color

    @property
    def coins(self):
        return self.__coins

    @property
    def value(self):
        return self.__value

    @property
    def effect(self):
        return self.__effect

    @property
    def info(self):
        info = {
            "uuid": self.__uuid,
            "name": self.__name,
            "color": self.__color,
            "coins": self.__coins,
            "value": self.__value,
            "effect": self.__effect
        }

        return info


class ClassCharacter:
    def __init__(self, uuid=None, order=0, name="", effect=None):
        self.__uuid = uuid
        self.__order = order
        self.__name = name
        self.__effect = effect

    def __eq__(self, other):  # override default equals behavior
        return self.__order == other.__order and self.__name == other.__name and self.__effect == other.__effect

    @property
    def uuid(self):
        return self.__uuid

    @property
    def order(self):
        return self.__order

    @property
    def name(self):
        return self.__name

    @property
    def effect(self):
        return self.__effect

    @property
    def info(self):
        info = {
            "uuid": self.__uuid,
            "order": self.__order,
            "name": self.__name,
            "effect": self.__effect
        }

        return info


class ClassDeckDistrict:
    def __init__(self, amount=0, card=None):
        self.__amount = amount
        self.__card = card

    def __eq__(self, other):  # override default equals behavior
        return self.__card == other.__card

    @property
    def amount(self):
        return self.__amount

    @amount.setter
    def amount(self, value):
        if isinstance(value, int):
            self.__amount = value

    @property
    def card(self):
        return self.__card

    @card.setter
    def card(self, value):
        if isinstance(value, ClassDistrict):
            self.__card = value

    @property
    def info(self):
        info = {
            "amount": self.__amount,
            "card": self.__card.info,
        }

        return info


class ClassCard:
    def __init__(self, ):
        self.__districts_red = [
            ClassDeckDistrict(3, ClassDistrict(name="Tower", color="red", coins=1, value=1, effect=None)),
            ClassDeckDistrict(3, ClassDistrict(name="Prison", color="red", coins=2, value=2, effect=None)),
            ClassDeckDistrict(3, ClassDistrict(name="Tournament field", color="red", coins=3, value=3, effect=None)),
            ClassDeckDistrict(2, ClassDistrict(name="Stronghold", color="red", coins=5, value=5, effect=None))
        ]

        self.__districts_yellow = [
            ClassDeckDistrict(5, ClassDistrict(name="Domain", color="yellow", coins=3, value=3, effect=None)),
            ClassDeckDistrict(4, ClassDistrict(name="Castle", color="yellow", coins=4, value=4, effect=None)),
            ClassDeckDistrict(3, ClassDistrict(name="Palace", color="yellow", coins=5, value=5, effect=None))
        ]

        self.__districts_blue = [
            ClassDeckDistrict(3, ClassDistrict(name="Temple", color="blue", coins=1, value=1, effect=None)),
            ClassDeckDistrict(3, ClassDistrict(name="Church", color="blue", coins=2, value=2, effect=None)),
            ClassDeckDistrict(3, ClassDistrict(name="Monastery", color="blue", coins=3, value=3, effect=None)),
            ClassDeckDistrict(2, ClassDistrict(name="Cathedral", color="blue", coins=5, value=5, effect=None))
        ]

        self.__districts_green = [
            ClassDeckDistrict(5, ClassDistrict(name="Tavern", color="green", coins=1, value=1, effect=None)),
            ClassDeckDistrict(4, ClassDistrict(name="Marketplace", color="green", coins=2, value=2, effect=None)),
            ClassDeckDistrict(3, ClassDistrict(name="Shop", color="green", coins=2, value=2, effect=None)),
            ClassDeckDistrict(3, ClassDistrict(name="Company", color="green", coins=3, value=3, effect=None)),
            ClassDeckDistrict(2, ClassDistrict(name="Town hall", color="green", coins=5, value=5, effect=None))
        ]

        self.__districts_purple = [
            ClassDeckDistrict(1, ClassDistrict(name="Court of miracles", color="purple", coins=2, value=2, effect=None)),
            ClassDeckDistrict(2, ClassDistrict(name="Dungeon", color="purple", coins=3, value=3, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name="Powder tower", color="purple", coins=3, value=3, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name="Lighthouse", color="purple", coins=3, value=3, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name="Museum", color="purple", coins=4, value=4, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name="Treasury", color="purple", coins=4, value=4, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name="Casino", color="purple", coins=5, value=5, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name="Laboratory", color="purple", coins=5, value=5, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name="Graveyard", color="purple", coins=5, value=5, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name="Library", color="purple", coins=6, value=6, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name="Magicians' school", color="purple", coins=6, value=6, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name="Dragon gate", color="purple", coins=6, value=8, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name="University", color="purple", coins=6, value=8, effect=None))
        ]

        self.__unique_districts = [
            self.__districts_red,
            self.__districts_yellow,
            self.__districts_blue,
            self.__districts_green,
            self.__districts_purple
        ]

    def get_districts(self, separate=True):
        districts = []

        for districts_color in self.__unique_districts:  # go through each district color group
            for unique_district in districts_color:  # go through each unique district
                if separate:  # check if cards need to be separate (not by amount)
                    for index in range(unique_district.amount):  # for the specified amount
                        districts.append(unique_district.card)  # add card to list
                else:  # cards need to be by amount
                    districts.append(unique_district)  # add card to list

        return districts

    def get_characters(self):
        characters = [
            ClassCharacter(order=1, name="Assassin", effect="Kill another character. The killed character's turn is skipped."),
            ClassCharacter(order=2, name="Thief", effect="Steal all coins from another character at the beginning the turn."),
            ClassCharacter(order=3, name="Magician", effect="Trade all district in your hand with another player or discard districts in your hand and draw the same amount."),
            ClassCharacter(order=4, name="King", effect="Get king status. Start choosing a character next round. Get coins for each yellow district you have built."),
            ClassCharacter(order=5, name="Bishop", effect="Warlord cannot destroy your buildings. Get coins for each blue district you have built."),
            ClassCharacter(order=6, name="Merchant", effect="Get one coin. Get coins for each green district you have built."),
            ClassCharacter(order=7, name="Architect", effect="Can build up to three districts. Draw two district cards."),
            ClassCharacter(order=8, name="Warlord", effect="Destroy one building of another character by paying one less coin than what was paid. Get coins for each red district you have built.")
        ]

        return characters
