import random, enum

from pprint import pprint

from copy import deepcopy

from api.classes import player
from api.classes.card import ClassDeckDistrict, ClassCharacterName


class ClassState(enum.Enum):
    created = "created"
    started = "started"
    selection_phase = "selection_phase"
    turn_phase = "turn_phase"
    finished = "finished"


class ClassSettings:
    def __init__(self, min_players=2, max_players=7, amount_starting_hand=4, amount_starting_coins=2, database_object=None):
        self.__min_players = min_players
        self.__max_players = max_players
        self.__amount_starting_hand = amount_starting_hand
        self.__amount_starting_coins = amount_starting_coins

        if database_object:  # check if parameters contain a database object
            self.__min_players = database_object.min_players
            self.__max_players = database_object.max_players
            self.__amount_starting_hand = database_object.amount_starting_hand
            self.__amount_starting_coins = database_object.amount_starting_coins

    @property
    def min_players(self):
        return self.__min_players

    @property
    def max_players(self):
        return self.__max_players

    @property
    def amount_starting_hand(self):
        return self.__amount_starting_hand

    @property
    def amount_starting_coins(self):
        return self.__amount_starting_coins


class ClassGame:
    def __init__(self, uuid=None, created="", description="", state="", players=None, amount_players=0, characters_open=0, characters_closed=0, characters_per_player=0, deck_characters=None, deck_districts=None, discard_pile=None, eight_districts_built=False, character_turn="", round=1, possible_characters=None, removed_characters=None, settings=None, database_object=None):
        if players is None:
            players = []

        if deck_characters is None:
            deck_characters = []

        if deck_districts is None:
            deck_districts = []

        if discard_pile is None:
            discard_pile = []

        if possible_characters is None:
            possible_characters = []

        if removed_characters is None:
            removed_characters = []

        if settings is None:
            settings = ClassSettings()

        self.__uuid = uuid
        self.__created = created

        self.__description = description

        self.__state = state

        self.__players = players
        self.__amount_players = amount_players

        self.__characters_open = characters_open
        self.__characters_closed = characters_closed
        self.__characters_per_player = characters_per_player

        self.__deck_characters = deck_characters
        self.__deck_districts = deck_districts
        self.__discard_pile = discard_pile

        self.__eight_districts_built = eight_districts_built
        self.__character_turn = character_turn
        self.__round = round
        self.__possible_characters = possible_characters
        self.__removed_characters = removed_characters

        self.__settings = settings

        if database_object:  # check if parameters contain a database object
            self.__uuid = database_object.uuid
            self.__created = database_object.created
            self.__description = database_object.description
            self.__state = database_object.state
            self.__amount_players = database_object.amount_players
            self.__character_turn = database_object.character_turn
            self.__round = database_object.round

    @property
    def uuid(self):
        return self.__uuid

    @property
    def created(self):
        return self.__created

    @property
    def description(self):
        return self.__description

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, value):
        self.__state = value

    @property
    def amount_players(self):
        return self.__amount_players

    @amount_players.setter
    def amount_players(self, value):
        if isinstance(value, int):
            self.__amount_players = value

    @property
    def characters_open(self):
        return self.__characters_open

    @property
    def characters_closed(self):
        return self.__characters_closed

    @property
    def characters_per_player(self):
        return self.__characters_per_player

    @property
    def players(self):
        return self.__players

    @players.setter
    def players(self, value):
        self.__players = value

    @property
    def deck_characters(self):
        return self.__deck_characters

    @deck_characters.setter
    def deck_characters(self, value):
        self.__deck_characters = value

    @property
    def deck_districts(self):
        return self.__deck_districts

    @deck_districts.setter
    def deck_districts(self, value):
        self.__deck_districts = value

    @property
    def discard_pile(self):
        return self.__discard_pile

    @discard_pile.setter
    def discard_pile(self, value):
        self.__discard_pile = value

    @property
    def eight_districts_built(self):
        return self.__eight_districts_built

    @eight_districts_built.setter
    def eight_districts_built(self, value):
        self.__eight_districts_built = value

    @property
    def character_turn(self):
        return self.__character_turn

    @character_turn.setter
    def character_turn(self, value):
        self.__character_turn = value

    @property
    def round(self):
        return self.__round

    @round.setter
    def round(self, value):
        self.__round = value

    @property
    def possible_characters(self):
        return self.__possible_characters

    @possible_characters.setter
    def possible_characters(self, value):
        self.__possible_characters = value

    @property
    def removed_characters(self):
        return self.__removed_characters

    @removed_characters.setter
    def removed_characters(self, value):
        self.__removed_characters = value

    @property
    def settings(self):
        return self.__settings

    @settings.setter
    def settings(self, value):
        self.__settings = value

    @property
    def deck_districts_by_amount(self):
        return self.aggregate_cards_by_name(self.__deck_districts)

    @property
    def info(self):
        info = {
            "uuid": self.__uuid,
            "created": self.__created,
            "description": self.__description,
            "state": self.__state,
            "players": self.__players,
            "amount_players": self.__amount_players,
            "characters_open": self.__characters_open,
            "characters_closed": self.__characters_closed,
            "characters_per_player": self.__characters_per_player,
            "deck_characters": self.__deck_characters,
            "deck_districts": self.__deck_districts,
            "discard_pile": self.__discard_pile,
            "eight_districts_built": self.__eight_districts_built,
            "character_turn": self.__character_turn,
            "round": self.__round,
            "possible_characters": self.__possible_characters,
            "removed_characters": self.__removed_characters,
            "settings": self.__settings
        }

        return info

    def set_starting_king(self):
        index_king = random.randint(0, self.__amount_players - 1)  # randomly choose a king
        self.__players[index_king].king = True  # make a random player the king
        self.__players[index_king].select_expected = True  # king is expected to select character first in the selection phase

    def set_character_division(self):
        if self.__amount_players == 2:
            self.__characters_open = 0
            self.__characters_closed = 4
            self.__characters_per_player = 2

        if self.__amount_players == 3:
            self.__characters_open = 0
            self.__characters_closed = 2
            self.__characters_per_player = 2

        elif self.__amount_players == 4:
            self.__characters_open = 2
            self.__characters_closed = 2
            self.__characters_per_player = 1

        elif self.__amount_players == 5:
            self.__characters_open = 1
            self.__characters_closed = 2
            self.__characters_per_player = 1

        elif self.__amount_players == 6:
            self.__characters_open = 0
            self.__characters_closed = 2
            self.__characters_per_player = 1

        elif self.__amount_players == 7:
            self.__characters_open = 0
            self.__characters_closed = 1
            self.__characters_per_player = 1

    def __draw_card(self, deck, card_index=None):  # draw card from deck
        if isinstance(card_index, int):
            cards_in_deck = len(deck)

            if cards_in_deck > 1:
                drawn_card = deck.pop(card_index)

            else:  # last card in deck
                drawn_card = deck.pop(0)

            return deck, drawn_card

        else:
            random_card_index = 0
            cards_in_deck = len(deck)

            if cards_in_deck > 1:
                random_card_index = random.randint(1, cards_in_deck - 1)

            drawn_card = deck.pop(random_card_index)

            return deck, drawn_card

    def draw_card_deck_characters(self, index):
        self.__deck_characters, drawn_card = self.__draw_card(self.__deck_characters, index)
        return drawn_card

    def draw_card_deck_districts(self):
        self.__deck_districts, drawn_card = self.__draw_card(self.__deck_districts, -1)  # -1 to draw card on top of deck
        return drawn_card

    def set_starting_coins_per_player(self):
        for player in self.__players:
            player.coins = self.__settings.amount_starting_coins

    def set_seat_per_player(self):
        self.__players = sorted(self.__players, key=lambda player: player.created, reverse=False)  # order players by created timestamp

        for index in range(self.__amount_players):  # go through each player
            self.__players[index].seat = index  # assign seat number

    def set_starting_hand_per_player(self):  # give each player a card for the amount of players there are
        for index in range(self.__settings.amount_starting_hand):
            for player in self.__players:
                drawn_card = self.draw_card_deck_districts()
                player.cards.append(drawn_card)

    def __remove_characters_for_round(self, characters):  # remove characters for this round
        characters_removed = []

        for index in range(self.__characters_open):  # for the amount of removed open characters
            random.shuffle(characters)  # shuffle deck
            characters, drawn_character_card = self.__draw_card(characters)  # draw a character card
            drawn_character_card.open = True  # character card needs to be open
            characters_removed.append(drawn_character_card)  # remove the drawn character

        return characters_removed

    def __remove_character_for_round(self, characters, open):
        random.shuffle(characters)  # shuffle deck
        characters, drawn_card = self.__draw_card(characters)  # draw character card
        drawn_card.open = open  # set whether character card needs to be open

        return characters, drawn_card

    def set_initial_possible_and_removed_characters(self):
        possible_characters = list(filter(lambda character: character.name != ClassCharacterName.king.value, self.__deck_characters))  # remove king from deck with characters
        character_king = list(filter(lambda character: character.name == ClassCharacterName.king.value, self.__deck_characters))[0]  # separated king

        removed_characters = []
        for index in range(self.__characters_open):  # for the amount of removed open characters
            possible_characters, removed_character = self.__remove_character_for_round(possible_characters, True)  # get removed open character and remaining possible characters
            removed_characters.append(removed_character)  # add removed character to list or removed characters

        possible_characters.append(character_king)  # add king back to possible characters

        possible_characters, removed_character = self.__remove_character_for_round(possible_characters, False)  # get removed closed character and remaining possible characters
        removed_characters.append(removed_character)  # add removed character to list or removed characters

        self.__possible_characters = possible_characters  # set possible characters
        self.__removed_characters = removed_characters  # set removed characters

    def remove_character_from_possible_characters(self, name):
        possible_characters = list(filter(lambda character: character.name != name, self.__possible_characters))  # remove selected character from possible characters
        selected_character = list(filter(lambda character: character.name == name, self.__possible_characters))[0]  # separate selected character

        self.__possible_characters = possible_characters  # set possible characters

        return selected_character

    def aggregate_cards_by_name(self, cards):
        aggregation = {}

        for card in cards:  # go through cards
            if card.name not in aggregation.keys():  # check if card is not in aggregation obejct
                aggregation[card.name] = ClassDeckDistrict(1, card)  # add card by amount to aggregation
            else:  # card is in aggregation
                new_deck_district = aggregation[card.name]  # get card from aggregation
                new_deck_district.amount += 1  # increase amount
                aggregation[card.name] = new_deck_district  # update card in aggregation

        return list(map(lambda district: district, aggregation.values()))  # return deck of cards with updated card amount
