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
    def __init__(self, active=False, description="", main=False, used=False, used_by=None):
        if used_by is None:
            used_by = []

        self.__active = active  # is it an ability the player needs to activate (active) or does it happen automatically (passive)
        self.__description = description  # description of the ability
        self.__main = main  # is it the character's main ability | false if it's the ability to receive aditional income per district of a certain or if it's a district ability
        self.__used = used  # has the ability been used this turn
        self.__used_by = used_by  # list of cards which use this ability

    @property
    def active(self):
        return self.__active

    @property
    def description(self):
        return self.__description

    @property
    def main(self):
        return self.__main

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
            "main": self.__main,
            "used": self.__used,
            "used_by": self.__used_by
        }

        return info


class ClassDistrict:
    def __init__(self, uuid=None, name="", color="", gold=0, value=0, effect=None, ability_used=False, amount=1, database_object=None):
        if effect is None:
            effect = []

        self.__uuid = uuid
        self.__name = name
        self.__color = color
        self.__gold = gold
        self.__value = value
        self.__effect = effect
        self.__ability_used = ability_used
        self.__amount = amount

        if database_object:  # check if parameters contain a database object
            self.__uuid = database_object.uuid
            self.__name = database_object.name
            self.__ability_used = database_object.ability_used
            self.__amount = database_object.amount

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
    def gold(self):
        return self.__gold

    @property
    def value(self):
        return self.__value

    @property
    def effect(self):
        return self.__effect

    @effect.setter
    def effect(self, value):
        self.__effect = value

    @property
    def ability_used(self):
        return self.__ability_used

    @ability_used.setter
    def ability_used(self, value):
        self.__ability_used = value

    @property
    def amount(self):
        return self.__amount

    @amount.setter
    def amount(self, value):
        self.__amount = value

    @property
    def info(self):
        effects = []
        for effect in self.__effect:
            effects.append(effect.info)

        info = {
            "uuid": self.__uuid,
            "name": self.__name,
            "color": self.__color,
            "gold": self.__gold,
            "value": self.__value,
            "effect": effects,
            "ability_used": self.__ability_used,
            "amount": self.__amount
        }

        return info


class ClassCharacter:
    def __init__(self, uuid=None, order=0, name="", effect=None, open=False, assassinated=False, robbed=False, built=0, max_built=1, income_received=False, ability_used=False, ability_additional_income_used=False, database_object=None):
        if effect is None:
            effect = []

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
        self.__ability_used = ability_used
        self.__ability_additional_income_used = ability_additional_income_used

        if database_object:  # check if parameters contain a database object
            self.__uuid = database_object.uuid
            self.__name = database_object.name
            self.__open = database_object.open
            self.__assassinated = database_object.assassinated
            self.__robbed = database_object.robbed
            self.__built = database_object.built
            self.__income_received = database_object.income_received
            self.__ability_used = database_object.ability_used
            self.__ability_additional_income_used = database_object.ability_additional_income_used

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
    def ability_used(self):
        return self.__ability_used

    @ability_used.setter
    def ability_used(self, value):
        self.__ability_used = value

    @property
    def ability_additional_income_used(self):
        return self.__ability_additional_income_used

    @ability_additional_income_used.setter
    def ability_additional_income_used(self, value):
        self.__ability_additional_income_used = value

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
            "income_received": self.__income_received,
            "ability_used": self.__ability_used,
            "ability_additional_income_used": self.__ability_additional_income_used
        }

        return info


class ClassCard:
    def __init__(self):
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
                         main=True,
                         used_by=[
                             ClassCharacterName.assassin.value
                         ]),
            ClassAbility(active=True,
                         description="Pick a character you wish to rob. Take all of the robbed character's gold at the beginning of their turn.",
                         main=True,
                         used_by=[
                             ClassCharacterName.thief.value
                         ]),
            ClassAbility(active=True,
                         description="Trade all districts in your hand with another player or discard districts in your hand to draw the same amount from the deck of districts.",
                         main=True,
                         used_by=[
                             ClassCharacterName.magician.value
                         ]),
            ClassAbility(active=False,
                         description="Receive the crown. You are the first player to choose your character during the next round. If you are killed, you will receive the crown at the end of the round.",
                         main=True,
                         used_by=[
                             ClassCharacterName.king.value
                         ]),
            ClassAbility(active=False,
                         description="The districts in your city cannot be destroyed by the warlord until the end of this round.",
                         main=True,
                         used_by=[
                             ClassCharacterName.bishop.value
                         ]),
            ClassAbility(active=False,
                         description="Receive one additional coin after receiving your character's income.",
                         main=True,
                         used_by=[
                             ClassCharacterName.merchant.value
                         ]),
            ClassAbility(active=False,
                         description="Draw two additional cards from the deck of districts after receiving your character's income.",
                         main=True,
                         used_by=[
                             ClassCharacterName.architect.value
                         ]),
            ClassAbility(active=False,
                         description="Your building limit is three this turn.",
                         main=True,
                         used_by=[
                             ClassCharacterName.architect.value
                         ]),
            ClassAbility(active=True,
                         description="Destroy one district in your or another player's city by paying one less coin than the cost of the district.",
                         main=True,
                         used_by=[
                             ClassCharacterName.warlord.value
                         ])
        ]

        self.__district_abilities = [
            ClassAbility(active=False,
                         description="This district counts as a district color which is missing in your city.",
                         used_by=[
                             ClassDistrictName.haunted_quarter.value
                         ]),
            ClassAbility(active=False,
                         description="This district cannot be destroyed by the warlord.",
                         used_by=[
                             ClassDistrictName.keep.value
                         ]),
            ClassAbility(active=False,
                         description="This district is worth 8 points.",
                         used_by=[
                             ClassDistrictName.dragon_gate.value,
                             ClassDistrictName.university.value
                         ]),
            ClassAbility(active=False,
                         description="This district counts as the color of your character for abilities which gain resources for your colored districts.",
                         used_by=[
                             ClassDistrictName.school_of_magic.value
                         ]),
            ClassAbility(active=False,
                         description="This district increases the amount of cards you keep by one when you draw cards for your income.",
                         used_by=[
                             ClassDistrictName.library.value
                         ]),
            ClassAbility(active=False,
                         description="This district increases the amount of cards you draw by one when you draw cards for your income.",
                         used_by=[
                             ClassDistrictName.observatory.value
                         ]),
            ClassAbility(active=True,
                         description="Once per turn you can pay 3 gold to draw 2 cards.",
                         used_by=[
                             ClassDistrictName.smithy.value
                         ]),
            ClassAbility(active=True,
                         description="Once per turn you can discard a card to receive one coin.",
                         used_by=[
                             ClassDistrictName.laboratory.value
                         ]),
            ClassAbility(active=False,
                         description="The warlord needs to pay one more coin to destroy a district in your city.",
                         used_by=[
                             ClassDistrictName.great_wall.value
                         ])
        ]

        self.__districts_red = [
            ClassDistrict(name=ClassDistrictName.watchtower.value, color=ClassColor.red.value, gold=1, value=1, amount=3),
            ClassDistrict(name=ClassDistrictName.prison.value, color=ClassColor.red.value, gold=2, value=2, amount=3),
            ClassDistrict(name=ClassDistrictName.barracks.value, color=ClassColor.red.value, gold=3, value=3, amount=3),
            ClassDistrict(name=ClassDistrictName.fortress.value, color=ClassColor.red.value, gold=5, value=5, amount=2)
        ]

        self.__districts_yellow = [
            ClassDistrict(name=ClassDistrictName.manor.value, color=ClassColor.yellow.value, gold=3, value=3, amount=5),
            ClassDistrict(name=ClassDistrictName.castle.value, color=ClassColor.yellow.value, gold=4, value=4, amount=4),
            ClassDistrict(name=ClassDistrictName.palace.value, color=ClassColor.yellow.value, gold=5, value=5, amount=3)
        ]

        self.__districts_blue = [
            ClassDistrict(name=ClassDistrictName.temple.value, color=ClassColor.blue.value, gold=1, value=1, amount=3),
            ClassDistrict(name=ClassDistrictName.church.value, color=ClassColor.blue.value, gold=2, value=2, amount=3),
            ClassDistrict(name=ClassDistrictName.monastery.value, color=ClassColor.blue.value, gold=3, value=3, amount=3),
            ClassDistrict(name=ClassDistrictName.cathedral.value, color=ClassColor.blue.value, gold=5, value=5, amount=2)
        ]

        self.__districts_green = [
            ClassDistrict(name=ClassDistrictName.tavern.value, color=ClassColor.green.value, gold=1, value=1, amount=5),
            ClassDistrict(name=ClassDistrictName.market.value, color=ClassColor.green.value, gold=2, value=2, amount=4),
            ClassDistrict(name=ClassDistrictName.trading_post.value, color=ClassColor.green.value, gold=2, value=2, amount=3),
            ClassDistrict(name=ClassDistrictName.docks.value, color=ClassColor.green.value, gold=3, value=3, amount=3),
            ClassDistrict(name=ClassDistrictName.harbor.value, color=ClassColor.green.value, gold=4, value=4, amount=3),
            ClassDistrict(name=ClassDistrictName.town_hall.value, color=ClassColor.green.value, gold=5, value=5, amount=2)
        ]

        self.__districts_purple = [
            ClassDistrict(name=ClassDistrictName.haunted_quarter.value, color=ClassColor.purple.value, gold=2, value=2),
            ClassDistrict(name=ClassDistrictName.keep.value, color=ClassColor.purple.value, gold=3, value=3, amount=2),
            ClassDistrict(name=ClassDistrictName.observatory.value, color=ClassColor.purple.value, gold=5, value=5),
            ClassDistrict(name=ClassDistrictName.laboratory.value, color=ClassColor.purple.value, gold=5, value=5),
            ClassDistrict(name=ClassDistrictName.great_wall.value, color=ClassColor.purple.value, gold=6, value=6),
            ClassDistrict(name=ClassDistrictName.smithy.value, color=ClassColor.purple.value, gold=5, value=5),
            ClassDistrict(name=ClassDistrictName.library.value, color=ClassColor.purple.value, gold=6, value=6),
            ClassDistrict(name=ClassDistrictName.school_of_magic.value, color=ClassColor.purple.value, gold=6, value=6),
            ClassDistrict(name=ClassDistrictName.dragon_gate.value, color=ClassColor.purple.value, gold=6, value=8),
            ClassDistrict(name=ClassDistrictName.university.value, color=ClassColor.purple.value, gold=6, value=8)
        ]

        self.__districts_grouped_by_color = [
            self.__districts_red,
            self.__districts_yellow,
            self.__districts_blue,
            self.__districts_green,
            self.__districts_purple
        ]

    def get_districts(self):
        districts = []

        for districts_color in self.__districts_grouped_by_color:  # go through each district color group
            districts.extend(districts_color)  # add districts with that color to list

        for district in districts:  # go through districts
            district.effect = list(filter(lambda ability: district.name in ability.used_by, self.__district_abilities))  # add abilities used by the district

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
