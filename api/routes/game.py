import json

from api import api, Resource, swag_from, reqparse, request, expects_json

from api.controllers.game import *

from api.models.game import Game as game_db

from api.utils.helpers import *


class Games(Resource):
    @swag_from('../templates/index.yml', endpoint='/game')
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('sort_order', type=str, help='sort order')
        parser.add_argument('order_by', type=str, help='order by given value')
        parser.add_argument('limit', type=int, help='return limited amount of items, 0 to return all items')
        parser.add_argument('offset', type=int, help='return items starting from this index position')
        args = parser.parse_args(strict=True)

        return get_games(args['sort_order'], args['order_by'], args['limit'], args['offset'])


class Game(Resource):
    @swag_from('../templates/index.yml', endpoint='/game/{game_uuid}')
    def get(self, game_uuid):
        return get_game(str(game_uuid))


class GameCreate(Resource):
    @swag_from('../templates/index.yml', endpoint='/game/action.create')
    @expects_json(read_json('api/schemas/game/create.json'))
    def post(self):
        body = json.loads(request.data)
        description = body["description"]

        return create_game(str(description))


class GameJoin(Resource):
    @swag_from('../templates/index.yml', endpoint='/game/{game_uuid}/action.join')
    @expects_json(read_json('api/schemas/game/join.json'))
    def post(self, game_uuid):
        body = json.loads(request.data)
        name = body["name"]

        return join_game(str(game_uuid), str(name))


api.add_resource(Games, '/game')
api.add_resource(Game, '/game/<string:game_uuid>')
api.add_resource(GameCreate, '/game/action.create')
api.add_resource(GameJoin, '/game/<string:game_uuid>/action.join')
