from api import api, Resource, swag_from, reqparse

from api.controllers.deck_districts import *


class DeckDistricts(Resource):
    @swag_from('../templates/index.yml', endpoint='/game/{game_uuid}/deck_districts')
    def get(self, game_uuid):
        parser = reqparse.RequestParser()
        parser.add_argument('sort_order', type=str, help='sort order')
        parser.add_argument('order_by', type=str, help='order by given value')
        parser.add_argument('limit', type=int, help='return limited amount of items, 0 to return all items')
        parser.add_argument('offset', type=int, help='return items starting from this index position')
        args = parser.parse_args(strict=True)

        return get_deck_districts(str(game_uuid), args['sort_order'], args['order_by'], args['limit'], args['offset'])


api.add_resource(DeckDistricts, '/game/<string:game_uuid>/deck_districts')
