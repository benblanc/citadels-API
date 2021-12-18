from api import api, Resource, swag_from, reqparse

from api.controllers.cards import *


class Games(Resource):
    @swag_from('../templates/index.yml', endpoint='/game')
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('sort_order', type=str, help='sort order')
        parser.add_argument('limit', type=int, help='return limited amount of items')
        parser.add_argument('offset', type=int, help='return items starting from this index position')
        args = parser.parse_args(strict=True)

        return get_games(args['sort_order'], args['limit'], args['offset'])

api.add_resource(Games, '/game')