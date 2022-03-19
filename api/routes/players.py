import json

from api import api, Resource, swag_from, reqparse, request, expects_json

from api.controllers.players import *

from api.utils.helpers import *


class Players(Resource):
    @swag_from('../templates/index.yml', endpoint='/game/{game_uuid}/players')
    def get(self, game_uuid):
        parser = reqparse.RequestParser()
        parser.add_argument('sort_order', type=str, help='sort order')
        parser.add_argument('order_by', type=str, help='order by given value')
        parser.add_argument('limit', type=int, help='return limited amount of items, 0 to return all items')
        parser.add_argument('offset', type=int, help='return items starting from this index position')
        args = parser.parse_args(strict=True)

        return get_players(str(game_uuid), args['sort_order'], args['order_by'], args['limit'], args['offset'])


class Player(Resource):
    @swag_from('../templates/index.yml', endpoint='/game/{game_uuid}/players/{player_uuid}')
    def get(self, game_uuid, player_uuid):
        return get_player(str(game_uuid), str(player_uuid))


class PlayerBuild(Resource):
    @swag_from('../templates/index.yml', endpoint='/game/{game_uuid}/players/{player_uuid}/action.build')
    @expects_json(read_json('api/schemas/player/build.json'))
    def post(self, game_uuid, player_uuid):
        body = json.loads(request.data)
        name = body["name"]

        return build(str(game_uuid), str(player_uuid), str(name).lower())


class PlayerReceiveCoins(Resource):
    @swag_from('../templates/index.yml', endpoint='/game/{game_uuid}/players/{player_uuid}/action.receive_coins')
    def post(self, game_uuid, player_uuid):
        return receive_coins(str(game_uuid), str(player_uuid))


class PlayerDrawCards(Resource):
    @swag_from('../templates/index.yml', endpoint='/game/{game_uuid}/players/{player_uuid}/action.draw_cards')
    def post(self, game_uuid, player_uuid):
        return draw_cards(str(game_uuid), str(player_uuid))


class PlayerStart(Resource):
    @swag_from('../templates/index.yml', endpoint='/game/{game_uuid}/players/{player_uuid}/action.start')
    def post(self, game_uuid, player_uuid):
        return start_game(str(game_uuid), str(player_uuid))


class PlayerSelect(Resource):
    @swag_from('../templates/index.yml', endpoint='/game/{game_uuid}/players/{player_uuid}/action.select')
    @expects_json(read_json('api/schemas/player/select.json'))
    def post(self, game_uuid, player_uuid):
        body = json.loads(request.data)
        name = body["name"]
        remove = body["remove"]

        return select_character(str(game_uuid), str(player_uuid), str(name).lower(), str(remove).lower())


class PlayerKeepCard(Resource):
    @swag_from('../templates/index.yml', endpoint='/game/{game_uuid}/players/{player_uuid}/action.keep_card')
    @expects_json(read_json('api/schemas/player/keep_card.json'))
    def post(self, game_uuid, player_uuid):
        body = json.loads(request.data)
        name = body["name"]

        return keep_card(str(game_uuid), str(player_uuid), str(name).lower())


class PlayerCharacterUseAbility(Resource):
    @swag_from('../templates/index.yml', endpoint='/game/{game_uuid}/players/{player_uuid}/action.use_ability')
    @expects_json(read_json('api/schemas/player/use_ability.json'))
    def post(self, game_uuid, player_uuid):
        body = json.loads(request.data)
        main = body["main"]
        name_character = body["name"]["character"]
        name_districts = body["name"]["districts"]
        other_player_uuid = body["player_uuid"]

        if name_districts:  # check if not none
            name_districts = list(name_districts)

        return use_ability(str(game_uuid), str(player_uuid), bool(main), str(name_character), name_districts, str(other_player_uuid))


class PlayerEndTurn(Resource):
    @swag_from('../templates/index.yml', endpoint='/game/{game_uuid}/players/{player_uuid}/action.end_turn')
    def post(self, game_uuid, player_uuid):
        return end_turn(str(game_uuid), str(player_uuid))


api.add_resource(Players, '/game/<string:game_uuid>/players')
api.add_resource(Player, '/game/<string:game_uuid>/players/<string:player_uuid>')
api.add_resource(PlayerBuild, '/game/<string:game_uuid>/players/<string:player_uuid>/action.build')
api.add_resource(PlayerReceiveCoins, '/game/<string:game_uuid>/players/<string:player_uuid>/action.receive_coins')
api.add_resource(PlayerDrawCards, '/game/<string:game_uuid>/players/<string:player_uuid>/action.draw_cards')
api.add_resource(PlayerStart, '/game/<string:game_uuid>/players/<string:player_uuid>/action.start')
api.add_resource(PlayerSelect, '/game/<string:game_uuid>/players/<string:player_uuid>/action.select')
api.add_resource(PlayerKeepCard, '/game/<string:game_uuid>/players/<string:player_uuid>/action.keep_card')
api.add_resource(PlayerCharacterUseAbility, '/game/<string:game_uuid>/players/<string:player_uuid>/action.use_ability')
api.add_resource(PlayerEndTurn, '/game/<string:game_uuid>/players/<string:player_uuid>/action.end_turn')
