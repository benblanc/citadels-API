from tests.simulate_game.controllers import *

GAME_DESCRIPTION = "Test to simulate game and see how far it gets before breaking"

NUMBER_OF_PLAYERS = 4

GOLD_INCOME_LIMIT = 6

EXIT_AFTER_GAME_CREATION = False
EXIT_AFTER_CHARACTER_SELECTION = False

SKIP_MAIN_ABILITY = False
SKIP_SECONDARY_ABILITY = False

EXIT_ON_ROUND = 100


def __get_filtered_item(items, check_property, required_value):
    response = None

    filtered_items = list(filter(lambda item: item[check_property] == required_value, items))  # filter through items

    if filtered_items:  # check if there are items after filtering
        response = filtered_items[0]  # get the first filtered item

    return response


def __perform_selection(game_uuid):
    players = get_players(game_uuid)

    player_expected_to_select = __get_filtered_item(players, "select_expected", True)

    if player_expected_to_select:  # check if someone still needs to pick a character
        possible_characters = get_possible_characters(game_uuid)

        random_index = random.randint(0, len(possible_characters) - 1)

        keep_character = possible_characters[random_index]["name"]

        remove_character = ""

        if game["amount_players"] == 2:
            removed_characters = get_removed_characters(game_uuid)

            if len(removed_characters) > 1 or not player_expected_to_select["crown"]:  # first player to pick doesn't remove a character
                remove_character = possible_characters[0]["name"]

                if keep_character == remove_character:
                    remove_character = possible_characters[1]["name"]

        select_character(game_uuid, player_expected_to_select["uuid"], keep_character, remove_character)


def __get_cards_player_can_build(cards, districts_in_city, player_gold):
    cards_player_can_build = []

    for card in cards:
        if card["name"] not in districts_in_city:  # check if not already built
            card_full_info = get_card(card["name"])

            if player_gold >= card_full_info["gold"]:  # check if affordable
                cards_player_can_build.append(card["name"])

    return cards_player_can_build


def __receive_income(game_uuid, player_uuid, player_gold, player_building_names):
    if player_gold < GOLD_INCOME_LIMIT:
        receive_gold(game_uuid, player_uuid)

    else:
        draw_cards(game_uuid, player_uuid)

        drawn_cards = get_drawn_cards(game_uuid, player_uuid)

        drawn_card_names = []
        for card in drawn_cards:
            for index in range(card["amount"]):
                drawn_card_names.append(card["name"])

        keep_amount = 1

        if "library" in player_building_names:
            keep_amount += 1

        cards_to_keep = []
        for index in range(keep_amount):
            random_index = random.randint(0, len(drawn_card_names) - 1)
            name = drawn_card_names[random_index]
            cards_to_keep.append(name)
            drawn_card_names.remove(name)  # remove so len becomes smaller

        keep_card(game_uuid, player_uuid, cards_to_keep)


def __build_district(game_uuid, player_uuid, district):
    build(game_uuid, player_uuid, district)


def __use_secondary_ability(game_uuid, player_uuid, character_name):
    character_with_ability = [
        "king",
        "bishop",
        "merchant",
        "warlord"
    ]

    if character_name in character_with_ability:  # check if character can actually use the ability
        use_ability(game_uuid, player_uuid, main=False)


def __use_assassin_ability():
    characters = get_characters()

    random_index = random.randint(1, len(characters) - 1)

    return characters[random_index]["name"]  # character to kill


def __use_thief_ability(game_uuid):
    character_name = None

    characters = get_characters()

    can_be_robbed = False

    while not can_be_robbed:  # repeat until a character is picked who can be robbed
        random_index = random.randint(2, len(characters) - 1)

        character_name = characters[random_index]["name"]  # character to rob

        characters_in_round = []

        players = get_players(game_uuid)

        for player in players:
            player_characters = get_player_characters(game_uuid, player["uuid"])

            characters_in_round += player_characters  # add characters to the rest of characters of this round

        can_be_robbed = True  # temporarily assume character can be robbed

        character_to_rob = __get_filtered_item(characters_in_round, "name", character_name)  # get character to be robbed | as long as character is not assassinated it's okay if it's not in round

        if character_to_rob:  # check if character is in round
            if character_to_rob["assassinated"]:  # check if character is assassinated
                can_be_robbed = False

    return character_name


def __use_magician_ability(game_uuid, player_uuid):
    other_player_uuid = None
    use_character_ability = True

    amount_cards_in_own_hand = len(get_player_cards(game_uuid, player_uuid))

    highest_other_player_amount_cards_in_hand = 0

    players = get_players(game_uuid)

    for player in players:
        if player["uuid"] != player_uuid:  # skip yourself
            player_cards = get_player_cards(game_uuid, player["uuid"])

            if highest_other_player_amount_cards_in_hand < len(player_cards):
                highest_other_player_amount_cards_in_hand = len(player_cards)
                other_player_uuid = player["uuid"]

    if not highest_other_player_amount_cards_in_hand or highest_other_player_amount_cards_in_hand < amount_cards_in_own_hand:  # check if not 0 and more cards in player's hand than our own
        use_character_ability = False  # player changed their mind and doesn't want to use character's ability

    return other_player_uuid, use_character_ability


def __use_warlord_ability():
    use_character_ability = False  # player changed their mind and doesn't want to use character's ability
    return use_character_ability


def __use_main_ability(game_uuid, player_uuid, character_expected_to_play):
    use_character_ability = True
    character_name = None
    districts_name = None
    other_player_uuid = None

    if character_expected_to_play == "assassin":
        character_name = __use_assassin_ability()

    elif character_expected_to_play == "thief":
        character_name = __use_thief_ability(game_uuid)

    elif character_expected_to_play == "magician":
        other_player_uuid, use_character_ability = __use_magician_ability(game_uuid, player_uuid)

    elif character_expected_to_play == "warlord":
        use_character_ability = __use_warlord_ability()

    if use_character_ability:  # check if player changed their mind and doesn't want to activate ability
        use_ability(game_uuid, player_uuid, main=True, character_name=character_name, districts_name=districts_name, other_player_uuid=other_player_uuid)


def __use_district_ability(game_uuid, player_uuid, name, buildings, player_cards):
    district = __get_filtered_item(buildings, "name", name)

    if district:
        if not district["ability_used"]:
            card_to_discard = ""

            if name == "laboratory":
                random_index = random.randint(0, len(player_cards) - 1)

                card_to_discard = player_cards[random_index]["name"]

            use_district_ability(game_uuid, player_uuid, name, card_to_discard)

    return True


def __perform_turn(game_uuid):
    skip_main_ability = False
    skip_secondary_ability = False
    skip_smithy_ability = False
    skip_laboratory_ability = False

    # go through all players
    # find out which player has which character
    # loop over the characters
    # while character has not ended its turn, keep on playing its turn | while game["current_character"] == player_character: keep looping

    game = get_game(game_uuid)

    players = get_players(game_uuid)

    for player in players:
        player_characters = get_player_characters(game_uuid, player["uuid"])

        character_turn = __get_filtered_item(player_characters, "name", game["character_turn"])

        if character_turn:  # check if player has the character who is expected to play a turn
            character_expected_to_play = character_turn
            player_character_turn_name = character_expected_to_play["name"]

            while player_character_turn_name == game["character_turn"]:
                player = get_player(game_uuid, player["uuid"])

                character = get_character(player_character_turn_name)

                player_cards = get_player_cards(game_uuid, player["uuid"])

                player_buildings = get_player_buildings(game_uuid, player["uuid"])

                player_building_names = list(map(lambda building: building["name"], player_buildings))

                cards_player_can_build = __get_cards_player_can_build(player_cards, player_building_names, player["gold"])

                if not character_expected_to_play["income_received"]:  # check if character has not yet received an income
                    __receive_income(game_uuid, player["uuid"], player["gold"], player_building_names)

                elif character_expected_to_play["income_received"] and character_expected_to_play["built"] < character["max_built"] and cards_player_can_build:  # check if character has received an income, building limit not yet reached and there are districts the player can actually build
                    __build_district(game_uuid, player["uuid"], cards_player_can_build[0])

                elif not character_expected_to_play["ability_additional_income_used"] and not skip_secondary_ability:  # check if character has not yet used its second ability to gain income per colored district
                    skip_secondary_ability = True  # skip using the ability next time the script wants to try
                    __use_secondary_ability(game_uuid, player["uuid"], player_character_turn_name)

                elif not character_expected_to_play["ability_used"] and not skip_main_ability:  # check if character has not yet used its main ability
                    skip_main_ability = True  # skip using the ability next time the script wants to try
                    __use_main_ability(game_uuid, player["uuid"], player_character_turn_name)

                elif "smithy" in player_building_names and player["gold"] > 3 and not skip_smithy_ability:  # check if player has the smithy and has enough gold to use its effect and ability not yet used
                    if random.choice([0, 1]):  # 50% chance to actually use the district ability
                        skip_smithy_ability = __use_district_ability(game_uuid, player["uuid"], "smithy", player_buildings, player_cards)

                elif "laboratory" in player_building_names and player_cards and not skip_laboratory_ability:  # check if player has the laboratory and player has cards to discard and ability not yet used
                    if random.choice([0, 1]):  # 50% chance to actually use the district ability
                        skip_laboratory_ability = __use_district_ability(game_uuid, player["uuid"], "laboratory", player_buildings, player_cards)

                else:  # nothing else to do so end turn
                    skip_main_ability = False  # reset flag
                    skip_secondary_ability = False  # reset flag

                    end_turn(game_uuid, player["uuid"])

                game = get_game(game_uuid)

                player_characters = get_player_characters(game_uuid, player["uuid"])

                character_expected_to_play = __get_filtered_item(player_characters, "name", game["character_turn"])

                if not character_expected_to_play:  # check if not none
                    break  # exit while loop to enter the loop as a new character


if __name__ == '__main__':
    game_uuid = create_game(GAME_DESCRIPTION)["uuid"]

    player_name = "Wubby"

    for index in range(NUMBER_OF_PLAYERS):
        join_game(game_uuid, player_name + " " + str(index))

    players = get_players(game_uuid)

    host = __get_filtered_item(players, "hosting", True)

    start_game(game_uuid, host["uuid"])

    game = get_game(game_uuid)

    if EXIT_AFTER_GAME_CREATION:
        print("EXIT_AFTER_GAME_CREATION")
        exit(0)

    while game["state"] != "finished":
        if game["state"] == "selection_phase":
            __perform_selection(game_uuid)

        if game["state"] == "turn_phase":
            if EXIT_AFTER_CHARACTER_SELECTION:
                print("EXIT_AFTER_CHARACTER_SELECTION")
                exit(0)

            if EXIT_ON_ROUND == game["round"]:
                print("EXIT_ON_ROUND")
                exit(0)

            __perform_turn(game_uuid)

        game = get_game(game_uuid)

    print("Game has finished!")
