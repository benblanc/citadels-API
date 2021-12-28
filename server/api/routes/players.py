import json

from api import api, Resource, swag_from, reqparse, request, expects_json

from api.controllers.players import *

from api.models.players import Players as players_db

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


api.add_resource(Players, '/game/<string:game_uuid>/players')
api.add_resource(Player, '/game/<string:game_uuid>/players/<string:player_uuid>')
