import random, enum

from pprint import pprint

from copy import deepcopy

from api.classes import player
from api.classes.card import ClassDeckDistrict


class ClassState(enum.Enum):
    created = "created"
    started = "started"
    dividing = "dividing"
    summoning = "summoning"
    finished = "finished"


class ClassSettings:
    def __init__(self, min_players=2, max_players=7, amount_starting_hand=4, amount_starting_coins=2):
        self.__min_players = min_players
        self.__max_players = max_players
        self.__amount_starting_hand = amount_starting_hand
        self.__amount_starting_coins = amount_starting_coins

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
    def __init__(self, uuid=None, created="", name="", description="", state="", players=None, amount_players=0, characters_open=0, characters_closed=0, characters_per_player=0, deck_characters=None, deck_districts=None, discard_pile=None, eight_districts_built=False, round=1, possible_characters=None, removed_characters=None, settings=None):
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

        self.__name = name
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
        self.__round = round
        self.__possible_characters = possible_characters
        self.__removed_characters = removed_characters

        self.__settings = settings

    @property
    def uuid(self):
        return self.__uuid

    @property
    def created(self):
        return self.__created

    @property
    def name(self):
        return self.__name

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
        districts = {}

        for district in self.__deck_districts:
            if district.name not in districts.keys():
                districts[district.name] = ClassDeckDistrict(1, district)
            else:
                new_deck_district = districts[district.name]
                new_deck_district.amount += 1
                districts[district.name] = new_deck_district

        return list(map(lambda district: district[1], districts.items()))  # index 0 is key, index 1 is value

    @property
    def info(self):
        info = {
            "uuid": self.__uuid,
            "created": self.__created,
            "name": self.__name,
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
            "round": self.__round,
            "possible_characters": self.__possible_characters,
            "removed_characters": self.__removed_characters,
            "settings": self.__settings
        }

        return info

    def set_starting_king(self):
        index_king = random.randint(0, self.__amount_players - 1)  # randomly choose a king
        self.__players[index_king].king = True  # make a random player the king

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
        self.__deck_districts, drawn_card = self.__draw_card(self.__deck_districts)
        return drawn_card

    def set_starting_coins_per_player(self):
        for player in self.__players:
            player.coins = self.__settings.amount_starting_coins

    def set_starting_hand_per_player(self):  # give each player a card for the amount of players there are
        for index in range(self.__settings.amount_starting_hand):
            for player in self.__players:
                drawn_card = self.draw_card_deck_districts()
                player.cards.append(drawn_card)

    def __remove_characters_for_round(self, characters):  # remove characters for this round
        characters_removed = []

        for index in range(self.__characters_unused):
            random.shuffle(characters)  # shuffle deck
            characters, drawn_card = self.__draw_card(characters)
            characters_removed.append(drawn_card)

        return characters_removed

    def __prepare_pickable_characters(self):
        # remove king from deck with characters
        characters = list(filter(lambda x: x.name != "King", self.__deck_characters))
        character_king = list(filter(lambda x: x.name == "King", self.__deck_characters))[0]

        # get removed characters for this round
        characters_removed = self.__remove_characters_for_round(characters)

        # add king back to pickable characters
        characters.append(character_king)

        return characters, characters_removed

    def __get_index_character(self, order_number):
        for index_character in range(len(self.__deck_characters)):  # go through each character
            if self.__deck_characters[index_character].order == order_number:  # find character with given order number
                return index_character  # return character index

    def set_character_per_player(self):
        # prepare character picking
        self.__deck_characters, self.__removed_characters = self.__prepare_pickable_characters()

        # sort lists with remaining characters
        self.__deck_characters = sorted(self.__deck_characters, key=lambda x: x.order, reverse=False)

        # sort list with removed characters
        self.__removed_characters = sorted(self.__removed_characters, key=lambda x: x.order, reverse=False)

        # set possible characters
        self.__possible_characters = deepcopy(self.__deck_characters)

        print("Characters removed for this round:")
        for character in self.__removed_characters:
            print("%s) %s" % (character.order, character.name))
        print("=================================================================")

        # check who is king at the moment
        current_king = list(filter(lambda x: x.king == True, self.__players))[0]

        # establish choosing order
        choosing_order_normal = list(range(0, self.__amount_players))
        choosing_order = choosing_order_normal[current_king.index:] + choosing_order_normal[:current_king.index]

        # distribute character(s)
        for index in range(self.__characters_per_player):  # 2-3 players allows more characters per player
            for index_choosing_order in choosing_order:  # let each player pick (king starts)
                print("Hello player ", index_choosing_order + 1)
                print("Characters the players can choose from:")
                for character in self.__deck_characters:
                    print("%s) %s" % (character.order, character.name))

                order_number = int(input("Pick a character for this round by entering the order number: "))

                index_character = self.__get_index_character(order_number)

                drawn_card = self.draw_card_deck_characters(index_character)

                self.__players[index_choosing_order].character.append(drawn_card)

                print("=================================================================")

    def remove_character_per_player(self):
        for player in self.__players:
            player.character = []

    def use_character_effect(self):
        pass

    def start_player_turn(self, player_index, character):
        player = self.__players[player_index]

        # income phase
        print("-------------- INCOME PHASE --------------")

        input_income = None
        input_income_possible = [1, 2]

        while input_income not in input_income_possible:
            print("Hello, %s! What will you take as your income?" % player.name)
            print("1) Take 2 coins\n"
                  "2) Draw 2 district cards, choose one and discard the other")
            input_income = int(input("Your choice: "))

            if input_income == 1:
                player.coins += 2  # increase coins by 2

            elif input_income == 2:
                drawn_cards = []

                for index in range(2):  # draw 2 cards
                    drawn_cards.append(self.draw_card_deck_districts())

                print("Drawn cards:")
                for card in drawn_cards:
                    pprint(card.info)

                input_drawn_district = None
                input_drawn_district_possible = [1, 2]

                while input_drawn_district not in input_drawn_district_possible:
                    print("Which of these two cards will you keep?")
                    print("1) First card\n"
                          "2) Second card")
                    input_drawn_district = int(input("Your choice: "))

                    chosen_card = drawn_cards.pop(input_drawn_district - 1)

                    player.cards.append(chosen_card)  # add chosen card to hand

                    self.__discard_pile.append(drawn_cards[0])  # add other card to discard pile

                # print("cards left in deck districts: %s" % len(self.__deck_districts))
                # print("cards in discard pile: %s" % len(self.__discard_pile))

        # print("-----------------------------------------------------------------")
        # pprint(self.__players[player_index].info)
        #
        # for card in self.__players[player_index].cards:
        #     pprint(card.info)
        #
        # print("-----------------------------------------------------------------")
        #
        # for card in self.__discard_pile:
        #     pprint(card.info)

        # main phase
        print("-------------- MAIN PHASE --------------")

        while True:
            print("What will you do during your turn?")
            print("1) Build a district\n"
                  "2) Use character's ability\n"
                  "3) Show player info\n"
                  "4) End turn")
            input_main = int(input("Your choice: "))

            if input_main == 1:
                while not player.flag_built:  # while the player has not built a districtl
                    print("Which of these districts in your hand will you build?")
                    print("0) Nevermind, I do not want to build a district")
                    for index in range(len(player.cards)):
                        print("%s) %s" % (index + 1, player.cards[index].name))
                        pprint(player.cards[index].info)

                    input_build = int(input("Your choice: ")) - 1

                    if input_build != -1:  # player wants to build

                        if player.coins < player.cards[input_build].coins:  # if player has not enough coins
                            print("You do not have enough coins to build this district.")

                        else:  # player has enough coins
                            district = player.cards.pop(input_build)  # remove card from hand
                            player.buildings.append(district)  # add to districts built
                            player.coins -= district.coins  # remove coins from player
                            player.flag_built = True  # set player has built flag
                            break

                    else:  # player does not want to build
                        break

            elif input_main == 2:
                print("You use your character's ability.")

                if character.order == 1:
                    # TODO: fix error where you are currently do not have the correct districts in hand (other player's)
                    # TODO: figure out how to set assassinated_flag since player can have 2 characters

                    # print("Which character do you want to kill?")
                    # for index in range(len(self.__possible_characters)):
                    #     print("%s) %s" % (index + 1, self.__possible_characters[index].name))
                    #
                    # input_build = int(input("Your choice: ")) - 1
                    #
                    # print(input_build)
                    pass

                elif character.order == 2:
                    pass

                elif character.order == 3:
                    pass

                elif character.order == 4:
                    pass

                elif character.order == 5:
                    pass

                elif character.order == 6:
                    pass

                elif character.order == 7:
                    pass

                elif character.order == 8:
                    pass

            elif input_main == 3:
                print("Here is the info for each player.")
                for player in self.players:
                    pprint(player.info)
                    print("----------------------------------------------")

            elif input_main == 4:
                player.flag_built = False  # reset player has built flag
                print("You end your turn.")
                break

        # end phase
        print("-------------- END PHASE --------------")

        print("=================================================================")
