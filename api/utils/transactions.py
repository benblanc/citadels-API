from api.classes.card import *
from api.classes.game import *
from api.classes.player import *

from api.models.buildings import Buildings as buildings_db
from api.models.cards import Cards as cards_db
from api.models.characters import Characters as characters_db
from api.models.deck_characters import DeckCharacters as deck_characters_db
from api.models.deck_discard_pile import DeckDiscardPile as deck_discard_pile_db
from api.models.deck_districts import DeckDistricts as deck_districts_db
from api.models.drawn_cards import DrawnCards as drawn_cards_db
from api.models.game import Game as game_db
from api.models.players import Players as players_db
from api.models.possible_characters import PossibleCharacters as possible_characters_db
from api.models.removed_characters import RemovedCharacters as removed_characters_db
from api.models.settings import Settings as settings_db

from api.services import database

from api.utils import helpers


def write_game(game):
    return database.write_row_to_db(game_db(
        uuid=game.uuid,
        created=game.created,
        description=game.description,
        state=game.state,
        amount_players=game.amount_players,
        character_turn=game.character_turn,
        round=game.round,
        log=game.log))


def write_settings(game_uuid, settings):
    return database.write_row_to_db(settings_db(
        uuid=helpers.create_uuid(),
        min_players=settings.min_players,
        max_players=settings.max_players,
        amount_starting_hand=settings.amount_starting_hand,
        amount_starting_coins=settings.amount_starting_coins,
        game_uuid=game_uuid))


def write_district_to_deck_districts(game_uuid, district):
    return database.write_row_to_db(deck_districts_db(
        uuid=helpers.create_uuid(),
        name=district.name,
        amount=district.amount,
        game_uuid=game_uuid))


def write_character_to_deck_characters(game_uuid, character):
    return database.write_row_to_db(deck_characters_db(
        uuid=helpers.create_uuid(),
        name=character.name,
        open=character.open,
        assassinated=character.assassinated,
        robbed=character.robbed,
        built=character.built,
        income_received=character.income_received,
        ability_used=character.ability_used,
        ability_additional_income_used=character.ability_additional_income_used,
        game_uuid=game_uuid))


def write_player(game_uuid, player):
    return database.write_row_to_db(players_db(
        uuid=player.uuid,
        created=player.created,
        name=player.name,
        hosting=player.hosting,
        seat=player.seat,
        coins=player.coins,
        king=player.king,
        protected=player.protected,
        select_expected=player.select_expected,
        city_first_completed=player.city_first_completed,
        score=player.score,
        game_uuid=game_uuid))


def write_character_to_possible_characters(game_uuid, character):
    return database.write_row_to_db(possible_characters_db(
        uuid=helpers.create_uuid(),
        name=character.name,
        open=character.open,
        assassinated=character.assassinated,
        robbed=character.robbed,
        built=character.built,
        income_received=character.income_received,
        ability_used=character.ability_used,
        ability_additional_income_used=character.ability_additional_income_used,
        game_uuid=game_uuid))


def write_character_to_removed_characters(game_uuid, character):
    return database.write_row_to_db(removed_characters_db(
        uuid=helpers.create_uuid(),
        name=character.name,
        open=character.open,
        assassinated=character.assassinated,
        robbed=character.robbed,
        built=character.built,
        income_received=character.income_received,
        ability_used=character.ability_used,
        ability_additional_income_used=character.ability_additional_income_used,
        game_uuid=game_uuid))


def write_character_to_player_characters(player_uuid, character):
    return database.write_row_to_db(characters_db(
        uuid=helpers.create_uuid(),
        name=character.name,
        open=character.open,
        assassinated=character.assassinated,
        robbed=character.robbed,
        built=character.built,
        income_received=character.income_received,
        ability_used=character.ability_used,
        ability_additional_income_used=character.ability_additional_income_used,
        player_uuid=player_uuid))


def write_card_to_table(table, uuid, card, player_table=False):
    if player_table:  # check if card is written to a player table
        return database.write_row_to_db(table(
            uuid=helpers.create_uuid(),
            name=card.name,
            amount=card.amount,
            player_uuid=uuid))
    else:  # card is written to a game table
        return database.write_row_to_db(table(
            uuid=helpers.create_uuid(),
            name=card.name,
            amount=card.amount,
            game_uuid=uuid))


def get_game(game_uuid):
    response = None

    game = game_db.query.get(game_uuid)

    if game:
        response = ClassGame(database_object=game)

    return response


def get_game_settings(game_uuid):
    response = None

    settings = settings_db.query.filter_by(game_uuid=game_uuid).first()

    if settings:
        response = ClassSettings(database_object=settings)

    return response


def get_game_deck_characters(game_uuid):
    response = []

    deck_characters = deck_characters_db.query.filter_by(game_uuid=game_uuid).all()

    if deck_characters:
        response = list(map(lambda character: ClassCharacter(database_object=character), deck_characters))

    return response


def get_game_deck_districts(game_uuid):
    response = []

    deck_districts = deck_districts_db.query.filter_by(game_uuid=game_uuid).all()

    if deck_districts:
        response = list(map(lambda district: ClassDistrict(database_object=district), deck_districts))

    return response


def get_game_discard_pile(game_uuid):
    response = []

    discard_pile = deck_discard_pile_db.query.filter_by(game_uuid=game_uuid).all()

    if discard_pile:
        response = list(map(lambda district: ClassDistrict(database_object=district), discard_pile))

    return response


def get_game_possible_characters(game_uuid):
    response = []

    possible_characters = possible_characters_db.query.filter_by(game_uuid=game_uuid).all()

    if possible_characters:
        response = list(map(lambda character: ClassCharacter(database_object=character), possible_characters))

    return response


def get_game_removed_characters(game_uuid):
    response = []

    removed_characters = removed_characters_db.query.filter_by(game_uuid=game_uuid).all()

    if removed_characters:
        response = list(map(lambda character: ClassCharacter(database_object=character), removed_characters))

    return response


def get_players(game_uuid):
    response = []

    players = players_db.query.filter_by(game_uuid=game_uuid).all()

    if players:
        response = list(map(lambda player: ClassPlayer(database_object=player), players))

    return response


def get_player(player_uuid):
    response = None

    player = players_db.query.get(player_uuid)

    if player:
        response = ClassPlayer(database_object=player)

    return response


def get_player_characters(player_uuid):
    response = []

    characters = characters_db.query.filter_by(player_uuid=player_uuid).all()

    if characters:
        response = list(map(lambda character: ClassCharacter(database_object=character), characters))

    return response


def get_player_buildings(player_uuid):
    response = []

    buildings = buildings_db.query.filter_by(player_uuid=player_uuid).all()

    if buildings:
        response = list(map(lambda district: ClassDistrict(database_object=district), buildings))

    return response


def get_player_cards(player_uuid):
    response = []

    cards = cards_db.query.filter_by(player_uuid=player_uuid).all()

    if cards:
        response = list(map(lambda district: ClassDistrict(database_object=district), cards))

    return response


def get_player_drawn_cards(player_uuid):
    response = []

    drawn_cards = drawn_cards_db.query.filter_by(player_uuid=player_uuid).all()

    if drawn_cards:
        response = list(map(lambda district: ClassDistrict(database_object=district), drawn_cards))

    return response


def get_all_from_query(table, sort_order, order_by, limit, offset, uuid="", player_table=False, default_sort_order="asc", default_order_by="name", default_limit=0, default_offset=0):
    if sort_order:  # check if not none
        default_sort_order = sort_order

    if order_by:  # check if not none
        default_order_by = order_by

    if limit:  # check if not none
        default_limit = limit

    if offset:  # check if not none
        default_offset = offset

    if default_order_by == "name":
        sort = table.name
    elif default_order_by == 'created':
        sort = table.created
    elif default_order_by == "uuid":
        sort = table.uuid

    if default_sort_order == "asc":
        sort = sort.asc()
    elif default_sort_order == "desc":
        sort = sort.desc()

    if uuid:  # check if query should be filtered on uuid
        if default_limit == 0:  # check if there is no limit
            if player_table:  # check if table should be filtered on player uuid
                response = table.query.filter_by(player_uuid=uuid).order_by(sort).offset(default_offset).all()
            else:  # table should be filtered on game uuid
                response = table.query.filter_by(game_uuid=uuid).order_by(sort).offset(default_offset).all()

        else:  # there is a limit
            if player_table:  # check if table should be filtered on player uuid
                response = table.query.filter_by(player_uuid=uuid).order_by(sort).limit(default_limit).offset(default_offset).all()
            else:  # table should be filtered on game uuid
                response = table.query.filter_by(game_uuid=uuid).order_by(sort).limit(default_limit).offset(default_offset).all()

    else:  # query should not be filtered on uuid
        if default_limit == 0:  # check if there is no limit
            if player_table:  # check if table should be filtered on player uuid
                response = table.query.order_by(sort).offset(default_offset).all()
            else:  # table should be filtered on game uuid
                response = table.query.order_by(sort).offset(default_offset).all()

        else:  # there is a limit
            if player_table:  # check if table should be filtered on player uuid
                response = table.query.order_by(sort).limit(default_limit).offset(default_offset).all()
            else:  # table should be filtered on game uuid
                response = table.query.order_by(sort).limit(default_limit).offset(default_offset).all()

    return response
