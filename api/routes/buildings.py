import json

from api import api, Resource, swag_from, reqparse, request, expects_json

from api.controllers.buildings import *

from api.utils.helpers import *


class Buildings(Resource):
    @swag_from('../templates/index.yml', endpoint='/game/{game_uuid}/players/{player_uuid}/buildings')
    def get(self, game_uuid, player_uuid):
        parser = reqparse.RequestParser()
        parser.add_argument('sort_order', type=str, help='sort order')
        parser.add_argument('order_by', type=str, help='order by given value')
        parser.add_argument('limit', type=int, help='return limited amount of items, 0 to return all items')
        parser.add_argument('offset', type=int, help='return items starting from this index position')
        args = parser.parse_args(strict=True)

        return get_buildings(str(game_uuid), str(player_uuid), args['sort_order'], args['order_by'], args['limit'], args['offset'])


class PlayerBuildingUseAbility(Resource):
    @swag_from('../templates/index.yml', endpoint='/game/{game_uuid}/players/{player_uuid}/buildings/{name}/action.use_ability')
    @expects_json(read_json('api/schemas/building/use_ability.json'))
    def post(self, game_uuid, player_uuid, name):
        body = json.loads(request.data)
        target_name = body["name"]

        print(game_uuid)
        print(player_uuid)
        print(name)
        print(target_name)

        return use_ability(str(game_uuid), str(player_uuid), str(name), str(target_name))


api.add_resource(Buildings, '/game/<string:game_uuid>/players/<string:player_uuid>/buildings')
api.add_resource(PlayerBuildingUseAbility, '/game/<string:game_uuid>/players/<string:player_uuid>/buildings/<string:name>/action.use_ability')
