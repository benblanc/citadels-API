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


class ClassCard:
    def __init__(self):
        self.__districts_red = [
            {"amount": 3, "card": ClassDistrict("Tower", "red", 1, 1, None)},
            {"amount": 3, "card": ClassDistrict("Prison", "red", 2, 2, None)},
            {"amount": 3, "card": ClassDistrict("Tournament field", "red", 3, 3, None)},
            {"amount": 2, "card": ClassDistrict("Stronghold", "red", 5, 5, None)}
        ]

        self.__districts_yellow = [
            {"amount": 5, "card": ClassDistrict("Domain", "yellow", 3, 3, None)},
            {"amount": 4, "card": ClassDistrict("Castle", "yellow", 4, 4, None)},
            {"amount": 3, "card": ClassDistrict("Palace", "yellow", 5, 5, None)}
        ]

        self.__districts_blue = [
            {"amount": 3, "card": ClassDistrict("Temple", "blue", 1, 1, None)},
            {"amount": 3, "card": ClassDistrict("Church", "blue", 2, 2, None)},
            {"amount": 3, "card": ClassDistrict("Monastery", "blue", 3, 3, None)},
            {"amount": 2, "card": ClassDistrict("Cathedral", "blue", 5, 5, None)}
        ]

        self.__districts_green = [
            {"amount": 5, "card": ClassDistrict("Tavern", "green", 1, 1, None)},
            {"amount": 4, "card": ClassDistrict("Marketplace", "green", 2, 2, None)},
            {"amount": 3, "card": ClassDistrict("Shop", "green", 2, 2, None)},
            {"amount": 3, "card": ClassDistrict("Company", "green", 3, 3, None)},
            {"amount": 2, "card": ClassDistrict("Town hall", "green", 5, 5, None)}
        ]

        self.__districts_purple = [
            {"amount": 1, "card": ClassDistrict("Court of miracles", "purple", 2, 2, None)},
            {"amount": 2, "card": ClassDistrict("Dungeon", "purple", 3, 3, None)},
            {"amount": 1, "card": ClassDistrict("Powder tower", "purple", 3, 3, None)},
            {"amount": 1, "card": ClassDistrict("Lighthouse", "purple", 3, 3, None)},
            {"amount": 1, "card": ClassDistrict("Museum", "purple", 4, 4, None)},
            {"amount": 1, "card": ClassDistrict("Treasury", "purple", 4, 4, None)},
            {"amount": 1, "card": ClassDistrict("Casino", "purple", 5, 5, None)},
            {"amount": 1, "card": ClassDistrict("Laboratory", "purple", 5, 5, None)},
            {"amount": 1, "card": ClassDistrict("Graveyard", "purple", 5, 5, None)},
            {"amount": 1, "card": ClassDistrict("Library", "purple", 6, 6, None)},
            {"amount": 1, "card": ClassDistrict("Magicians' school", "purple", 6, 6, None)},
            {"amount": 1, "card": ClassDistrict("Dragon gate", "purple", 6, 8, None)},
            {"amount": 1, "card": ClassDistrict("University", "purple", 6, 8, None)}
        ]

        self.__unique_districts = [
            self.__districts_red,
            self.__districts_yellow,
            self.__districts_blue,
            self.__districts_green,
            self.__districts_purple
        ]

    def get_districts(self):
        districts = []

        for districts_color in self.__unique_districts:  # go through each district color group
            for unique_district in districts_color:  # go through each unique district
                for index in range(unique_district['amount']):  # for the specified amount
                    districts.append(unique_district['card'])  # add card to list

        return districts

    def get_characters(self):
        # characters = [
        #     ClassCharacter(1, "Assassin", None),
        #     ClassCharacter(2, "Thief", None),
        #     ClassCharacter(3, "Magician", None),
        #     ClassCharacter(4, "King", None),
        #     ClassCharacter(5, "Bishop", None),
        #     ClassCharacter(6, "Merchant", None),
        #     ClassCharacter(7, "Architect", None),
        #     ClassCharacter(8, "Warlord", None)
        # ]

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
