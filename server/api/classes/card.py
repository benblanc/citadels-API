import enum


class ClassColor(enum.Enum):
    red = "red"
    yellow = "yellow"
    blue = "blue"
    green = "green"
    purple = "purple"


class ClassDistrictName(enum.Enum):
    tower = "Tower"
    prison = "Prison"
    tournament_field = "Tournament field"
    stronghold = "Stronghold"

    domain = "Domain"
    castle = "Castle"
    palace = "Palace"

    temple = "Temple"
    church = "Church"
    monastery = "Monastery"
    cathedral = "Cathedral"

    tavern = "Tavern"
    marketplace = "Marketplace"
    shop = "Shop"
    company = "Company"
    town_hall = "Town hall"

    court_of_miracles = "Court of miracles"
    dungeon = "Dungeon"
    powder_tower = "Powder tower"
    lighthouse = "Lighthouse"
    museum = "Museum"
    treasury = "Treasury"
    casino = "Casino"
    laboratory = "Laboratory"
    graveyard = "Graveyard"
    library = "Library"
    magicians_school = "Magicians' school"
    dragon_gate = "Dragon gate"
    university = "University"


class ClassCharacterName(enum.Enum):
    assassin = "Assassin"
    thief = "Thief"
    magician = "Magician"
    king = "King"
    bishop = "Bishop"
    merchant = "Merchant"
    architect = "Architect"
    warlord = "Warlord"


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
            ClassDeckDistrict(3, ClassDistrict(name=ClassDistrictName.tower.value, color=ClassColor.red.value, coins=1, value=1, effect=None)),
            ClassDeckDistrict(3, ClassDistrict(name=ClassDistrictName.prison.value, color=ClassColor.red.value, coins=2, value=2, effect=None)),
            ClassDeckDistrict(3, ClassDistrict(name=ClassDistrictName.tournament_field.value, color=ClassColor.red.value, coins=3, value=3, effect=None)),
            ClassDeckDistrict(2, ClassDistrict(name=ClassDistrictName.stronghold.value, color=ClassColor.red.value, coins=5, value=5, effect=None))
        ]

        self.__districts_yellow = [
            ClassDeckDistrict(5, ClassDistrict(name=ClassDistrictName.domain.value, color=ClassColor.yellow.value, coins=3, value=3, effect=None)),
            ClassDeckDistrict(4, ClassDistrict(name=ClassDistrictName.castle.value, color=ClassColor.yellow.value, coins=4, value=4, effect=None)),
            ClassDeckDistrict(3, ClassDistrict(name=ClassDistrictName.palace.value, color=ClassColor.yellow.value, coins=5, value=5, effect=None))
        ]

        self.__districts_blue = [
            ClassDeckDistrict(3, ClassDistrict(name=ClassDistrictName.temple.value, color=ClassColor.blue.value, coins=1, value=1, effect=None)),
            ClassDeckDistrict(3, ClassDistrict(name=ClassDistrictName.church.value, color=ClassColor.blue.value, coins=2, value=2, effect=None)),
            ClassDeckDistrict(3, ClassDistrict(name=ClassDistrictName.monastery.value, color=ClassColor.blue.value, coins=3, value=3, effect=None)),
            ClassDeckDistrict(2, ClassDistrict(name=ClassDistrictName.cathedral.value, color=ClassColor.blue.value, coins=5, value=5, effect=None))
        ]

        self.__districts_green = [
            ClassDeckDistrict(5, ClassDistrict(name=ClassDistrictName.tavern.value, color=ClassColor.green.value, coins=1, value=1, effect=None)),
            ClassDeckDistrict(4, ClassDistrict(name=ClassDistrictName.marketplace.value, color=ClassColor.green.value, coins=2, value=2, effect=None)),
            ClassDeckDistrict(3, ClassDistrict(name=ClassDistrictName.shop.value, color=ClassColor.green.value, coins=2, value=2, effect=None)),
            ClassDeckDistrict(3, ClassDistrict(name=ClassDistrictName.company.value, color=ClassColor.green.value, coins=3, value=3, effect=None)),
            ClassDeckDistrict(2, ClassDistrict(name=ClassDistrictName.town_hall.value, color=ClassColor.green.value, coins=5, value=5, effect=None))
        ]

        self.__districts_purple = [
            ClassDeckDistrict(1, ClassDistrict(name=ClassDistrictName.court_of_miracles.value, color=ClassColor.purple.value, coins=2, value=2, effect=None)),
            ClassDeckDistrict(2, ClassDistrict(name=ClassDistrictName.dungeon.value, color=ClassColor.purple.value, coins=3, value=3, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name=ClassDistrictName.powder_tower.value, color=ClassColor.purple.value, coins=3, value=3, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name=ClassDistrictName.lighthouse.value, color=ClassColor.purple.value, coins=3, value=3, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name=ClassDistrictName.museum.value, color=ClassColor.purple.value, coins=4, value=4, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name=ClassDistrictName.treasury.value, color=ClassColor.purple.value, coins=4, value=4, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name=ClassDistrictName.casino.value, color=ClassColor.purple.value, coins=5, value=5, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name=ClassDistrictName.laboratory.value, color=ClassColor.purple.value, coins=5, value=5, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name=ClassDistrictName.graveyard.value, color=ClassColor.purple.value, coins=5, value=5, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name=ClassDistrictName.library.value, color=ClassColor.purple.value, coins=6, value=6, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name=ClassDistrictName.magicians_school.value, color=ClassColor.purple.value, coins=6, value=6, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name=ClassDistrictName.dragon_gate.value, color=ClassColor.purple.value, coins=6, value=8, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name=ClassDistrictName.university.value, color=ClassColor.purple.value, coins=6, value=8, effect=None))
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
            ClassCharacter(order=1, name=ClassCharacterName.assassin.value, effect="Kill another character. The killed character's turn is skipped."),
            ClassCharacter(order=2, name=ClassCharacterName.thief.value, effect="Steal all coins from another character at the beginning the turn."),
            ClassCharacter(order=3, name=ClassCharacterName.magician.value, effect="Trade all district in your hand with another player or discard districts in your hand and draw the same amount."),
            ClassCharacter(order=4, name=ClassCharacterName.king.value, effect="Get king status. Start choosing a character next round. Get coins for each yellow district you have built."),
            ClassCharacter(order=5, name=ClassCharacterName.bishop.value, effect="Warlord cannot destroy your buildings. Get coins for each blue district you have built."),
            ClassCharacter(order=6, name=ClassCharacterName.merchant.value, effect="Get one coin. Get coins for each green district you have built."),
            ClassCharacter(order=7, name=ClassCharacterName.architect.value, effect="Can build up to three districts. Draw two district cards."),
            ClassCharacter(order=8, name=ClassCharacterName.warlord.value, effect="Destroy one building of another character by paying one less coin than what was paid. Get coins for each red district you have built.")
        ]

        return characters
