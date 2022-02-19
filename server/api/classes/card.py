import enum


class ClassColor(enum.Enum):
    red = "red"
    yellow = "yellow"
    blue = "blue"
    green = "green"
    purple = "purple"


class ClassDistrictName(enum.Enum):
    watchtower = "watchtower"
    prison = "prison"
    barracks = "barracks"
    fortress = "fortress"

    manor = "manor"
    castle = "castle"
    palace = "palace"

    temple = "temple"
    church = "church"
    monastery = "monastery"
    cathedral = "cathedral"

    tavern = "tavern"
    market = "market"
    trading_post = "trading post"
    docks = "docks"
    harbor = "harbor"
    town_hall = "town hall"

    haunted_quarter = "haunted quarter"
    keep = "keep"
    observatory = "observatory"
    laboratory = "laboratory"
    graveyard = "graveyard"
    smithy = "smithy"
    library = "library"
    school_of_magic = "school of magic"
    dragon_gate = "dragon gate"
    university = "university"

    great_wall = "great wall"
    quarry = "quarry"
    wishing_well = "wishing well"
    imperial_treasury = "imperial treasury"
    map_room = "map room"
    hospital = "hsopital"
    poor_house = "poor house"
    lighthouse = "lighthouse"
    park = "park"
    powder_tower = "powder tower"
    ballroom = "ballroom"
    factory = "factory"
    museum = "museum"
    clock_tower = "clock tower"
    throne_room = "throne room"


class ClassCharacterName(enum.Enum):
    assassin = "assassin"
    thief = "thief"
    magician = "magician"
    king = "king"
    bishop = "bishop"
    merchant = "merchant"
    architect = "architect"
    warlord = "warlord"


class ClassAbility():
    def __init__(self, active=False, description="", used=False, used_by=None):
        if used_by is None:
            used_by = []

        self.__active = active  # is it an ability the player needs to activate (active) or does it happen automatically (passive)
        self.__description = description  # description of the ability
        self.__used = used  # has the ability been used this turn
        self.__used_by = used_by  # list of cards which use this ability

    @property
    def active(self):
        return self.__active

    @property
    def description(self):
        return self.__description

    @property
    def used(self):
        return self.__used

    @property
    def used_by(self):
        return self.__used_by

    @property
    def info(self):
        info = {
            "active": self.__active,
            "description": self.__description,
            "used": self.__used,
            "used_by": self.__used_by
        }

        return info


class ClassDistrict:
    def __init__(self, uuid=None, name="", color="", coins=0, value=0, effect=None):
        self.__name = name
        self.__color = color
        self.__coins = coins
        self.__value = value
        self.__effect = effect
        self.__uuid = uuid

    def __eq__(self, other):  # override default equals behavior
        return self.__name == other.__name

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
    def __init__(self, uuid=None, order=0, name="", effect=None, open=False, assassinated=False, robbed=False, built=0, max_built=1, income_received=False, database_object=None):
        self.__uuid = uuid
        self.__order = order
        self.__name = name
        self.__effect = effect
        self.__open = open
        self.__assassinated = assassinated
        self.__robbed = robbed
        self.__built = built
        self.__max_built = max_built
        self.__income_received = income_received

        if database_object:  # check if parameters contain a database object
            self.__uuid = database_object.uuid
            self.__name = database_object.name
            self.__open = database_object.open
            self.__assassinated = database_object.assassinated
            self.__robbed = database_object.robbed
            self.__built = database_object.built
            self.__income_received = database_object.income_received

    def __eq__(self, other):  # override default equals behavior
        return self.__name == other.__name

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

    @effect.setter
    def effect(self, value):
        self.__effect = value

    @property
    def open(self):
        return self.__open

    @open.setter
    def open(self, value):
        self.__open = value

    @property
    def assassinated(self):
        return self.__assassinated

    @assassinated.setter
    def assassinated(self, value):
        self.__assassinated = value

    @property
    def robbed(self):
        return self.__robbed

    @robbed.setter
    def robbed(self, value):
        self.__robbed = value

    @property
    def built(self):
        return self.__built

    @built.setter
    def built(self, value):
        self.__built = value

    @property
    def max_built(self):
        return self.__max_built

    @property
    def income_received(self):
        return self.__income_received

    @income_received.setter
    def income_received(self, value):
        self.__income_received = value

    @property
    def info(self):
        effects = []
        for effect in self.__effect:
            effects.append(effect.info)

        info = {
            "uuid": self.__uuid,
            "order": self.__order,
            "name": self.__name,
            "effect": effects,
            "open": self.__open,
            "assassinated": self.__assassinated,
            "robbed": self.__robbed,
            "built": self.__built,
            "max_built": self.__max_built,
            "income_received": self.__income_received
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
        self.__character_abilities = [
            ClassAbility(active=True,
                         description="You receive one coin for each district in your city with the same color as this card.",
                         used_by=[
                             ClassCharacterName.king.value,
                             ClassCharacterName.bishop.value,
                             ClassCharacterName.merchant.value,
                             ClassCharacterName.warlord.value
                         ]),
            ClassAbility(active=True,
                         description="Pick a character you wish to kill. The killed character's turn is skipped.",
                         used_by=[
                             ClassCharacterName.assassin.value
                         ]),
            ClassAbility(active=True,
                         description="Pick a character you wish to rob. Take all of the robbed character's coins at the beginning of their turn.",
                         used_by=[
                             ClassCharacterName.thief.value
                         ]),
            ClassAbility(active=True,
                         description="Trade all districts in your hand with another player or discard districts in your hand to draw the same amount from the deck of districts.",
                         used_by=[
                             ClassCharacterName.magician.value
                         ]),
            ClassAbility(active=False,
                         description="Receive the crown. You are the first player to choose your character during the next round. If you are killed, you will receive the crown at the end of the round.",
                         used_by=[
                             ClassCharacterName.king.value
                         ]),
            ClassAbility(active=False,
                         description="The districts in your city cannot be destroyed by the warlord until the end of this round.",
                         used_by=[
                             ClassCharacterName.bishop.value
                         ]),
            ClassAbility(active=False,
                         description="Receive one additional coin after receiving your character's income.",
                         used_by=[
                             ClassCharacterName.merchant.value
                         ]),
            ClassAbility(active=False,
                         description="Draw two additional cards from the deck of districts after receiving your character's income.",
                         used_by=[
                             ClassCharacterName.architect.value
                         ]),
            ClassAbility(active=False,
                         description="Your building limit is three this turn.",
                         used_by=[
                             ClassCharacterName.architect.value
                         ]),
            ClassAbility(active=True,
                         description="Destroy one district in your or another player's city by paying one less coin than the cost of the district.",
                         used_by=[
                             ClassCharacterName.warlord.value
                         ])
        ]

        self.__districts_red = [
            ClassDeckDistrict(3, ClassDistrict(name=ClassDistrictName.watchtower.value, color=ClassColor.red.value, coins=1, value=1, effect=None)),
            ClassDeckDistrict(3, ClassDistrict(name=ClassDistrictName.prison.value, color=ClassColor.red.value, coins=2, value=2, effect=None)),
            ClassDeckDistrict(3, ClassDistrict(name=ClassDistrictName.barracks.value, color=ClassColor.red.value, coins=3, value=3, effect=None)),
            ClassDeckDistrict(2, ClassDistrict(name=ClassDistrictName.fortress.value, color=ClassColor.red.value, coins=5, value=5, effect=None))
        ]

        self.__districts_yellow = [
            ClassDeckDistrict(5, ClassDistrict(name=ClassDistrictName.manor.value, color=ClassColor.yellow.value, coins=3, value=3, effect=None)),
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
            ClassDeckDistrict(4, ClassDistrict(name=ClassDistrictName.market.value, color=ClassColor.green.value, coins=2, value=2, effect=None)),
            ClassDeckDistrict(3, ClassDistrict(name=ClassDistrictName.trading_post.value, color=ClassColor.green.value, coins=2, value=2, effect=None)),
            ClassDeckDistrict(3, ClassDistrict(name=ClassDistrictName.docks.value, color=ClassColor.green.value, coins=3, value=3, effect=None)),
            ClassDeckDistrict(3, ClassDistrict(name=ClassDistrictName.harbor.value, color=ClassColor.green.value, coins=4, value=4, effect=None)),
            ClassDeckDistrict(2, ClassDistrict(name=ClassDistrictName.town_hall.value, color=ClassColor.green.value, coins=5, value=5, effect=None))
        ]

        self.__districts_purple = [
            ClassDeckDistrict(1, ClassDistrict(name=ClassDistrictName.haunted_quarter.value, color=ClassColor.purple.value, coins=2, value=2, effect=None)),
            ClassDeckDistrict(2, ClassDistrict(name=ClassDistrictName.keep.value, color=ClassColor.purple.value, coins=3, value=3, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name=ClassDistrictName.observatory.value, color=ClassColor.purple.value, coins=5, value=5, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name=ClassDistrictName.laboratory.value, color=ClassColor.purple.value, coins=5, value=5, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name=ClassDistrictName.graveyard.value, color=ClassColor.purple.value, coins=5, value=5, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name=ClassDistrictName.smithy.value, color=ClassColor.purple.value, coins=5, value=5, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name=ClassDistrictName.library.value, color=ClassColor.purple.value, coins=6, value=6, effect=None)),
            ClassDeckDistrict(1, ClassDistrict(name=ClassDistrictName.school_of_magic.value, color=ClassColor.purple.value, coins=6, value=6, effect=None)),
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
            ClassCharacter(order=1, name=ClassCharacterName.assassin.value),
            ClassCharacter(order=2, name=ClassCharacterName.thief.value),
            ClassCharacter(order=3, name=ClassCharacterName.magician.value),
            ClassCharacter(order=4, name=ClassCharacterName.king.value),
            ClassCharacter(order=5, name=ClassCharacterName.bishop.value),
            ClassCharacter(order=6, name=ClassCharacterName.merchant.value),
            ClassCharacter(order=7, name=ClassCharacterName.architect.value, max_built=3),
            ClassCharacter(order=8, name=ClassCharacterName.warlord.value)
        ]

        for character in characters:  # go through characters
            character.effect = list(filter(lambda ability: character.name in ability.used_by, self.__character_abilities))  # add abilities used by the character

        return characters
