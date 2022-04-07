from api.responses.definitions import *


def bad_request(field):
    response = define_message("The {field} value is required.".format(field=field))

    return response, 400


def not_host():
    response = define_message("The player making the request is not the host.")

    return response, 400


def not_select_expected():
    response = define_message("The player making the request is not expected to select a character.")

    return response, 400


def not_enough_players():
    response = define_message("The game does not have enough players to start.")

    return response, 400


def enough_players():
    response = define_message("The game already has enough players to start.")

    return response, 400


def already_started():
    response = define_message("The game has already started.")

    return response, 400


def not_selection_phase():
    response = define_message("The game needs to be in the character selection phase.")

    return response, 400


def not_turn_phase():
    response = define_message("The game needs to be in the character turn phase.")

    return response, 400


def same_character():
    response = define_message("The requested character cannot be the same as the character to remove.")

    return response, 400


def not_character():
    response = define_message("The player making the request does not have the expected character.")

    return response, 400


def already_income_received():
    response = define_message("The player making the request has already received the income for this character.")

    return response, 400


def must_receive_income_to_end_turn():
    response = define_message("The player making the request must receive an income before ending the turn of this character.")

    return response, 400


def must_receive_income_to_build():
    response = define_message("The player making the request must receive an income before building a district.")

    return response, 400


def already_cards_drawn():
    response = define_message("The player making the request has already drawn the district cards for this character.")

    return response, 400


def no_cards_drawn():
    response = define_message("The player making the request has not yet drawn the district cards for this character.")

    return response, 400


def no_cards_in_hand():
    response = define_message("The player making the request has no district cards their hand.")

    return response, 400


def already_in_city():
    response = define_message("The player making the request already has the same district in their city.")

    return response, 400


def already_completed_city():
    response = define_message("The player making the request already has a completed city.")

    return response, 400


def building_limit():
    response = define_message("The player making the request has reached the building limit for this character.")

    return response, 400


def not_enough_gold():
    response = define_message("The player making the request does not have enough gold to perform the action.")

    return response, 400


def completed_city():
    response = define_message("The warlord cannot destroy a district in a completed city.")

    return response, 400


def already_used_ability(main=True):
    item = "main"

    if not main:  # check if not a main ability
        item = "additional income"

    response = define_message("The player making the request has already used the character's {item} ability this turn.".format(item=item))

    return response, 400


def not_enough_cards_to_discard(name):
    response = define_message("The player making the request does not have enough districts with the name {name} to discard.".format(name=name))

    return response, 400


def player_protected():
    response = define_message("The targeted player is protected from the warlord.")

    return response, 400


def cannot_rob():
    response = define_message("The assassin, thief or assassinated character cannot be robbed.")

    return response, 400


def not_keep():
    response = define_message("The keep cannot be destroyed by the warlord.")

    return response, 400


def too_many_cards_to_keep():
    response = define_message("The player making the request cannot keep this many cards.")

    return response, 400


def not_enough_drawn_cards(amount, name):
    response = define_message("The player making the request cannot keep {amount} copies of the {name} of their drawn cards.".format(amount=amount, name=name))

    return response, 400


def no_district_name():
    response = define_message("The player making the request did not provide a district name.")

    return response, 400


def no_target_district_name():
    response = define_message("The player making the request did not provide a target district name.")

    return response, 400


def already_used_district_ability():
    response = define_message("The player making the request has already used the district's ability this turn.")

    return response, 400


def not_found(item="item", plural=False):
    message = "The requested {item} is not found or does not exist.".format(item=item)

    if plural:  # check if message needs to be plural
        message = "The requested {item} are not found or do not exist.".format(item=item)

    response = define_message(message)

    return response, 404


def conflict(field):
    response = define_message("The {field} value causes issues.".format(field=field))

    return response, 409
