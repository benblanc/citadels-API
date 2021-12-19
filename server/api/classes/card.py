class ClassDistrict:
    def __init__(self, name, color, coins, value, effect):
        self.__name = name
        self.__color = color
        self.__coins = coins
        self.__value = value
        self.__effect = effect

    def __eq__(self, other):  # override default equals behavior
        return self.__name == other.__name and self.__color == other.__color and self.__coins == other.__coins and self.__value == other.__value and self.__effect == other.__effect

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
            "name": self.__name,
            "color": self.__color,
            "coins": self.__coins,
            "value": self.__value,
            "effect": self.__effect
        }

        return info


class ClassCharacter:
    def __init__(self, order, name, effect):
        self.__order = order
        self.__name = name
        self.__effect = effect

    def __eq__(self, other):  # override default equals behavior
        return self.__order == other.__order and self.__name == other.__name and self.__effect == other.__effect

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
            "order": self.__order,
            "name": self.__name,
            "effect": self.__effect
        }

        return info


class ClassDeckDistrict:
    def __init__(self, amount, card):
        self.__amount = amount
        self.__card = card

    @property
    def amount(self):
        return self.__amount

    @property
    def card(self):
        return self.__card


class ClassCard:
    def __init__(self):
        self.__districts_red = [
            ClassDeckDistrict(3, ClassDistrict("Tower", "red", 1, 1, None)),
            ClassDeckDistrict(3, ClassDistrict("Prison", "red", 2, 2, None)),
            ClassDeckDistrict(3, ClassDistrict("Tournament field", "red", 3, 3, None)),
            ClassDeckDistrict(2, ClassDistrict("Stronghold", "red", 5, 5, None))
        ]

        self.__districts_yellow = [
            ClassDeckDistrict(5, ClassDistrict("Domain", "yellow", 3, 3, None)),
            ClassDeckDistrict(4, ClassDistrict("Castle", "yellow", 4, 4, None)),
            ClassDeckDistrict(3, ClassDistrict("Palace", "yellow", 5, 5, None))
        ]

        self.__districts_blue = [
            ClassDeckDistrict(3, ClassDistrict("Temple", "blue", 1, 1, None)),
            ClassDeckDistrict(3, ClassDistrict("Church", "blue", 2, 2, None)),
            ClassDeckDistrict(3, ClassDistrict("Monastery", "blue", 3, 3, None)),
            ClassDeckDistrict(2, ClassDistrict("Cathedral", "blue", 5, 5, None))
        ]

        self.__districts_green = [
            ClassDeckDistrict(5, ClassDistrict("Tavern", "green", 1, 1, None)),
            ClassDeckDistrict(4, ClassDistrict("Marketplace", "green", 2, 2, None)),
            ClassDeckDistrict(3, ClassDistrict("Shop", "green", 2, 2, None)),
            ClassDeckDistrict(3, ClassDistrict("Company", "green", 3, 3, None)),
            ClassDeckDistrict(2, ClassDistrict("Town hall", "green", 5, 5, None))
        ]

        self.__districts_purple = [
            ClassDeckDistrict(1, ClassDistrict("Court of miracles", "purple", 2, 2, None)),
            ClassDeckDistrict(2, ClassDistrict("Dungeon", "purple", 3, 3, None)),
            ClassDeckDistrict(1, ClassDistrict("Powder tower", "purple", 3, 3, None)),
            ClassDeckDistrict(1, ClassDistrict("Lighthouse", "purple", 3, 3, None)),
            ClassDeckDistrict(1, ClassDistrict("Museum", "purple", 4, 4, None)),
            ClassDeckDistrict(1, ClassDistrict("Treasury", "purple", 4, 4, None)),
            ClassDeckDistrict(1, ClassDistrict("Casino", "purple", 5, 5, None)),
            ClassDeckDistrict(1, ClassDistrict("Laboratory", "purple", 5, 5, None)),
            ClassDeckDistrict(1, ClassDistrict("Graveyard", "purple", 5, 5, None)),
            ClassDeckDistrict(1, ClassDistrict("Library", "purple", 6, 6, None)),
            ClassDeckDistrict(1, ClassDistrict("Magicians' school", "purple", 6, 6, None)),
            ClassDeckDistrict(1, ClassDistrict("Dragon gate", "purple", 6, 8, None)),
            ClassDeckDistrict(1, ClassDistrict("University", "purple", 6, 8, None))
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
            ClassCharacter(1, "Assassin", "Kill another character. The killed character's turn is skipped."),
            ClassCharacter(2, "Thief", "Steal all coins from another character at the beginning the turn."),
            ClassCharacter(3, "Magician", "Trade all district in your hand with another player or discard districts in your hand and draw the same amount."),
            ClassCharacter(4, "King", "Get king status. Start choosing a character next round. Get coins for each yellow district you have built."),
            ClassCharacter(5, "Bishop", "Warlord cannot destroy your buildings. Get coins for each blue district you have built."),
            ClassCharacter(6, "Merchant", "Get one coin. Get coins for each green district you have built."),
            ClassCharacter(7, "Architect", "Can build up to three districts. Draw two district cards."),
            ClassCharacter(8, "Warlord", "Destroy one building of another character by paying one less coin than what was paid. Get coins for each red district you have built.")
        ]

        return characters
